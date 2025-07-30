# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

"""
A pipeline runner that lets you simulate the execution of a pipeline in a local Python environment.

It can be used to locally mimic the behavior of the AI Inference Server concerning loading and running inference pipelines.
This is a quick and easy way to find programming or configuration errors before deploying the package.
The local pipeline runner also lets you exercise your pipeline component by component. In other words, you can feed
single components with inputs and verify the output produced.
"""

import platform
import tempfile
import zipfile
import pkg_resources
import yaml
import joblib
import json
import venv
import subprocess
import logging
import datetime
import sys
import os
import re
import shutil
from pathlib import Path
from importlib import metadata as importlib_metadata
from typing import Union, Optional

from simaticai.helpers import calc_sha
from simaticai.helpers.pep508 import parse_requirements
from simaticai.helpers.reporter import PipelineRunnerReportWriter, ReportWriterHandler
from simaticai.packaging.constants import (
    REQUIREMENTS_TXT, TELEMETRY_YAML,
    PYTHON_PACKAGES, PYTHON_PACKAGES_ZIP, MSG_NOT_FOUND
)
from simaticai.testing.pipeline_validator import INVALID_PIPELINE_PACKAGE_MESSAGE
from simaticai.testing.data_stream import DataStream

RETURN_CODE_OK = 0b0
RETURN_CODE_DEPRECATED = 0b10001  # equals to 17

logging.basicConfig()
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

_runner_path = Path(__file__).parent

type_map = {
    'int': 'Integer',
    'float': 'Double',
    'bool': 'Boolean',
    'str': 'String'
}

def _relative_to(path1, path2):
    path1 = Path(path1).resolve().absolute()
    path2 = Path(path2).resolve().absolute()
    return path1.relative_to(path2)

class LocalPipelineRunner:
    """
    Simulates the execution of a pipeline in a local Python environment.

    Only works with a pipeline configuration package. Does not work with e.g. an edge configuration package.

    Restriction: only linear pipelines are supported where the pipeline input variables are only used by one component,
    each component uses only the outputs of the previous components, and the pipeline output only consists of variables from the last component.

    If the caller specifies no `path`, the working directory is temporary and is removed unless an error occurs.
    If the caller specifies a working directory with a `path` argument, the working directory is kept.
    This behavior can be overridden using boolean parameter `cleanup`.

    Currently, the pipeline runner supports both the current `process_input(data: dict)` entrypoint signature and the legacy
    `run(data: str)` signature. If both entrypoints are present, `process_input()` takes precedence. Please note however that
    `run()` is deprecated, and support for it will be removed in future versions of the pipeline runner.

    Args:
        packageZip (path-like): Path to the pipeline configuration package.
        path (path-like): Path to the working directory. If unset, a temporary directory is created.
        cleanup (bool): If set, the working directory is kept when True, and deleted when False. \
            If unset, a temporary working directory is removed, and an explicit working directory is kept. \
            When an error occurs in a component, the working directory is kept regardless of this value.
    """

    def __init__(self, packageZip: os.PathLike, path: Optional[os.PathLike] = None, cleanup: Optional[bool] = None, loglevel = logging.INFO):
        """
        Creates a new component LocalPipelineRunner for the provided pipeline configuration package.

        Only works with a pipeline configuration package. Does not work with e.g. an edge configuration package.

        Args:
            packageZip (path-like): Path to the pipeline configuration package.
            path (path-like): Path to the working directory. If unset a temporary directory will be created.
            cleanup (bool): If set, the working directory will be kept when True, and deleted when False. \
                If unset, a temporary working directory will be removed, and an explicit working directory will be kept. \
                When an error occurs in a component, the working directory will be kept regardless of this value.
        """
        self.package_zip: Path = Path(packageZip)
        self.path = path
        self.components = {}
        self.parameters = {}
        self.cleanup = cleanup
        self.log_level = loglevel
        self.workdir: Path

        self.report_writer = PipelineRunnerReportWriter()
        report_writer_handler = ReportWriterHandler(self.report_writer)
        _logger.addHandler(report_writer_handler)

    def __enter__(self):
        self.report_writer.set_package_zip_path(self.package_zip)
        timestamp = re.sub(r"[-:]", "", datetime.datetime.utcnow().isoformat(sep="_", timespec="seconds"))
        if self.path is not None:
            self.workdir = Path(self.path)
            self.workdir.mkdir(parents=True, exist_ok=True)
            self.cleanup = self.cleanup if self.cleanup is not None else False
        else:
            self.workdir = Path(tempfile.mkdtemp(prefix=f"LocalPipelineRunner_{timestamp}_"))
            self.cleanup = self.cleanup if self.cleanup is not None else True

        unzip_components = False
        with zipfile.ZipFile(self.package_zip) as zf:
            if 'runtime_config.yml' in zf.namelist():
                self.workdir = self.workdir / self.package_zip.stem
                zf.extractall(path=self.workdir)
                unzip_components = True
            else:
                zf.extractall(path=self.workdir)
                self.workdir = self.workdir / zf.namelist()[0]

        try:
            with open(self.workdir / "pipeline_config.yml") as cf:
                config = yaml.load(cf, Loader=yaml.FullLoader)

            components = config["dataFlowPipeline"].get("components", [])
            for component in components:
                component["context"] = None
                component["env_dir"] = self.workdir / component['name']
                self.components[component["name"]] = component

            if unzip_components:
                for component in components:
                    component_zip = f"{component['name']}_{component['version']}.zip"
                    with zipfile.ZipFile(self.workdir / 'components' / component_zip) as zf:
                        zf.extractall(path=self.workdir / component["name"])

            for parameter in config["dataFlowPipeline"].get("pipelineParameters", {}):
                self.parameters[parameter["name"]] = parameter

        except Exception:
            raise RuntimeError(INVALID_PIPELINE_PACKAGE_MESSAGE)

        return self

    def __exit__(self, exception_type, value, traceback):

        self.update_telemetry_data()
        self.report_writer.write_report()

        if self.cleanup:
            _logger.info("Removing local pipeline runner environment...")
            shutil.rmtree(self.workdir.parent)
        else:
            _logger.info(f"Leaving local pipeline runner environment in its final state at '{self.workdir}'")

    def collect_telemetry_data(self):
        """
        Collects telemetry data about the platform, environment, industrial AI packages, and pipeline.

        Returns:
            dict: A dictionary containing the telemetry data.
        """
        telemetry_data = {}

        telemetry_data["platform"] = {}
        telemetry_data["platform"]["os"] = platform.system()
        telemetry_data["platform"]["release"] = platform.release()
        telemetry_data["platform"]["python_version"] = platform.python_version()

        _logger.info(f"locals: {locals()}")
        telemetry_data["environment"] = {}
        telemetry_data["environment"]["jupyter"]        = any(k for k in locals() if k in ["__IPYTHON__", "get_ipython"])
        telemetry_data["environment"]["gitlab_ci"]      = True if "GITLAB_CI" in os.environ else MSG_NOT_FOUND
        telemetry_data["environment"]["azure_devops"]   = True if "TF_BUILD" in os.environ else MSG_NOT_FOUND
        telemetry_data["environment"]["github_actions"] = True if "GITHUB_ACTIONS" in os.environ else MSG_NOT_FOUND

        telemetry_data["industrial_ai"] = {}
        try:
            telemetry_data["industrial_ai"]["simaticai"] = pkg_resources.get_distribution("simaticai").version
        except pkg_resources.DistributionNotFound:
            telemetry_data["industrial_ai"]["simaticai"] = MSG_NOT_FOUND

        try:
            telemetry_data["industrial_ai"]["vep-template-sdk"] = pkg_resources.get_distribution("vep-template-sdk").version
        except pkg_resources.DistributionNotFound:
            telemetry_data["industrial_ai"]["vep-template-sdk"] = MSG_NOT_FOUND

        telemetry_data["pipeline"] = {}
        telemetry_data["pipeline"]["python_versions"] = list(set(self.components[component]['runtime']['version'] for component in self.components if self.components[component]['runtime']['type'] == 'python'))
        telemetry_data["pipeline"]["file_extensions"] = []
        for component_dir in [Path(self.workdir) / c for c in Path(self.workdir).rglob("*") if c.name in self.components.keys()]:
            excluded_dirs = set([component_dir / '.venv', component_dir / '__pyache__'])
            suffixes = list(set(f.suffix for f in component_dir.rglob("*") if not (any(excluded_dirs.intersection(f.parents)) or f.suffix in ["", ".zip", ".yml", ".yaml", ".html"])))
            for suffix in suffixes:
                if suffix not in telemetry_data["pipeline"]["file_extensions"]:
                    telemetry_data["pipeline"]["file_extensions"].append(suffix)

        return telemetry_data

    def update_telemetry_data(self):
        """
        Update the telemetry data and the package.

        This method updates the telemetry data by loading the existing data from a YAML file,
        or collecting new telemetry data if the file doesn't exist. It then updates the
        "last_run" field of the telemetry data with the current timestamp. The updated
        telemetry data is then written back to the YAML file.

        If the package contains a different version of the telemetry data file, a new package
        is created with the updated telemetry data. Otherwise, the existing package is
        overwritten with the new package containing the updated telemetry data.

        Returns:
            None
        """
        _logger.info("Updating telemetry data and the package")
        telemetry_path = self.workdir / "telemetry_data.yml"
        if telemetry_path.is_file():
            telemetry_data = yaml.safe_load(telemetry_path.read_text())
        else:
            telemetry_data = self.collect_telemetry_data()

        telemetry_data["pipeline"]["last_run"] = datetime.datetime.now().isoformat()
        telemetry_path.write_text(yaml.dump(telemetry_data))

        config_package = False
        with zipfile.ZipFile(self.package_zip, 'r') as zip_read:
            for file in zip_read.namelist():
                if TELEMETRY_YAML in file and file != TELEMETRY_YAML:
                    config_package = True
                    break

        new_zip_path = Path(self.package_zip).parent / f"{Path(self.package_zip).stem}_tested.zip"

        with zipfile.ZipFile(self.package_zip, 'r') as zip_read:
            with zipfile.ZipFile(new_zip_path, 'w') as zip_write:
                for file in zip_read.namelist():
                    if TELEMETRY_YAML not in file:
                        filepath = zip_read.extract(file, path=self.workdir)
                        zip_write.write(filepath, arcname=file)
                    else:
                        zip_write.write(telemetry_path, arcname=file)

        if config_package:
            shutil.copy(new_zip_path, self.package_zip)
        else:
            new_sha_path = Path(self.package_zip).parent / f"{Path(self.package_zip).stem}_tested.sha256"
            new_sha_path.write_text(calc_sha(new_zip_path))

    def _install_requirements(self, component, package_dir, no_index: bool = True):
        _logger.info("Installing requirements...")
        pip_report_file = component["env_dir"] / "pip_report.json"
        executable_path = _relative_to(component['bin_path'] / 'python', component["env_dir"])
        package_dir_path = _relative_to(package_dir, component["env_dir"])
        pip_report_file_path = _relative_to(pip_report_file, component["env_dir"])
        cmd = [
            f"{executable_path}",
            "-m", "pip", "install",
            "--no-warn-script-location",
            "-f", f"{package_dir_path}",
            "-r", REQUIREMENTS_TXT,
            "--report", f"{pip_report_file_path}"]
        if no_index:
            cmd += [ "--no-index" ]
        result = subprocess.run(cmd, cwd=component["env_dir"], text=True, stderr=subprocess.PIPE)
        if 0 == result.returncode and pip_report_file.is_file():
            self.report_writer.add_installed_packages(component["name"], pip_report_file)
        return result

    def _install_from_packages_zip(self, component, package_dir):
        result = self._install_requirements(component, package_dir, True)
        return 0 == result.returncode

    def _install_from_pypi_org(self, component, package_dir):
        return self._install_requirements(component, package_dir, False)

    def _init_component_venv(self, component: dict):
        """
        Creates a virtual environment in which the given component can run.

        Args:
            component (str): name of the selected component.
        """
        _logger.info(f"Creating virtual environment for component '{component['name']}'...")
        context_dir = component["env_dir"] / ".venv"
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(str(context_dir))
        component["context"] = builder.ensure_directories(context_dir)
        component["bin_path"] = Path(component["context"].bin_path).absolute()
        _logger.debug(f"Component bin path: {component['bin_path']}")

        _logger.info("Upgrading pip...")
        executable_path = _relative_to(component['bin_path'] / 'python', component["env_dir"])
        cmd = [f"{executable_path}", "-m", "pip", "install", "pip", "--upgrade"]
        result = subprocess.run(cmd, cwd=component["env_dir"], text=True, stderr=subprocess.PIPE)
        if result.returncode != 0:
            self.cleanup = False
            _logger.warning(f"Error upgrading pip:\n{result.stderr}")

        try:
            result = self._install_logmodule(component["bin_path"], component["env_dir"])
        except Exception as err:
            _logger.error(err)
            self.cleanup = False
            raise RuntimeError("The 'simaticai' Python package is either not installed or does not contain package 'log_module'.") from None
        if result.returncode != 0:
            self.cleanup = False
            raise RuntimeError(f"Error installing log_module:\n{result.stderr}")

        req_list = Path(component["env_dir"] / "requirements.list")
        req_list.touch(exist_ok=True)
        if Path(component["env_dir"] / REQUIREMENTS_TXT).is_file():
            dependencies, extra_index, index_url = parse_requirements(component["env_dir"] / REQUIREMENTS_TXT)
            requirements = "#".join(dependencies.keys())
            req_list.write_text(requirements)
        else:
            _logger.info(f"'{REQUIREMENTS_TXT}' was not found. No additional dependencies were installed.")
            return

        package_dir = component["env_dir"] / PYTHON_PACKAGES
        package_zip = component["env_dir"] / PYTHON_PACKAGES_ZIP

        _logger.info(f"Extracting {PYTHON_PACKAGES_ZIP}")
        if package_zip.is_file():
            with zipfile.ZipFile(package_zip) as zf:
                zf.extractall(path=package_dir.absolute())
        else:
            _logger.info(f"There is no {PYTHON_PACKAGES_ZIP} to extract.")
            package_dir.mkdir(parents=True, exist_ok=True)

        success = self._install_from_packages_zip(component, package_dir)
        if not success:
            msg = f"Warning! Could not install dependencies from {PYTHON_PACKAGES_ZIP}. "
            msg += "Trying to install them from pypi.org. The resulting Python environment "
            msg += "may be significantly different than the targeted Python environment on the Edge Device!"
            _logger.warning(msg)
            second_install_result = self._install_from_pypi_org(component, package_dir)
            if 0 != second_install_result.returncode:
                self.cleanup = False
                raise RuntimeError(f"Error installing requirements:\n{second_install_result.stderr}")

    @staticmethod
    def _install_logmodule(bin_path, env_dir):
        _logger.info("Installing LogModule...")
        try:
            package_paths = importlib_metadata.files("simaticai")
            assert package_paths is not None
            logger_wheel = [p for p in package_paths if 'log_module' in str(p)][0].locate()
        except Exception:
            from importlib.metadata import Distribution
            direct_url = Distribution.from_name("simaticai").read_text("direct_url.json")
            assert direct_url is not None
            direct_url = json.loads(direct_url)['url']
            direct_url = direct_url.replace('file://','')
            direct_url = Path(direct_url) / 'simaticai' / 'data'
            paths = list(direct_url.rglob('*.whl'))
            logger_wheel = [p for p in paths if 'log_module' in str(p)][0].resolve()

        cmd = [
            f"{bin_path / 'pip'}",
            "install",
            "--no-warn-script-location", logger_wheel, "joblib"
        ]
        return subprocess.run(cmd, cwd=env_dir, text=True, stderr=subprocess.PIPE)

    def run_component(self, name: str, data: Optional[Union[dict, list, DataStream]]) -> Optional[Union[dict, list]]:
        """
        Runs the component in its virtual environment with the given input.
        This environment is created according to `requirements.txt` in the package.
        Additionally 'joblib' and the mock `log_module` is automatically installed in this virtual environment.
        The input data can be a single input record in a dictionary or a batch of input records in a list of dictionaries,
        or a DataStream object which will produce the appropriate input data.
        The supplied input data is saved as `inputs.joblib` in the component runtime directory, and the output is saved as `output.joblib`.

        Args:
            name (str): The name of the component to be executed.
            data (dict or list): One or more input records for the component.

        Returns:
            dict / list: A list of dictionaries for outputs if there were no errors and field `ready` is true.
            If the input was a single dict, then a single dict (the first item of the list) or None if there is no output.

        """
        assert name in self.components, f"Invalid component name: {name}"
        component = self.components[name]

        assert component["runtime"]["type"] in ["python", "gpuruntime"], f"Can not run component '{name}': Runtime type is nor 'python' or 'gpuruntime'"

        input_payload_path: Path  = component["env_dir"] / "input.joblib"
        output_payload_path: Path = component["env_dir"] / "output.joblib"

        batch_input: bool  = component["batch"]["inputBatch"]  == "Yes" if component.get("batch") is not None else False
        batch_output: bool = component["batch"]["outputBatch"] == "Yes" if component.get("batch") is not None else False

        # Validate and serialize input payload
        assert data is not None, f"Can not run component '{name}' without input."
        result_is_list = True
        if isinstance(data, list):
            input_payload = data
        elif isinstance(data, DataStream):
            input_payload = [item for item in data]
        else:
            result_is_list = False
            input_payload = [data]
        validate_payload(input_payload, component["inputType"], batch_input)
        joblib.dump(input_payload, input_payload_path)
        self.report_writer.set_input_payload_length(name, len(input_payload))
        _logger.info(f"Input payload saved as '{input_payload_path}'")

        # Assemble command for runnig component
        if component['runtime']['type'] == 'python':
            # Version check for Python
            e_major, e_minor, _, _, _ = sys.version_info
            c_major, c_minor, *_ = tuple(str(component["runtime"]["version"]).split('.'))
            if f"{e_major}.{e_minor}" != f"{c_major}.{c_minor}":
                msg = f"The local python version ({e_major}.{e_minor}) and the python version defined for the component ({c_major}.{c_minor}) are different."
                msg += " Testing will be done using dependencies that corresponds to the python version of your development environment."
                msg += " Pipeline behavior on AI Inference Server might be different."
                _logger.warning(msg)

            if component["context"] is None:
                self._init_component_venv(component)
                shutil.copy(_runner_path / 'run_component.py', component["env_dir"])

            req_list_path = _relative_to(component["env_dir"] / "requirements.list", component["env_dir"])
            json_params = json.dumps({param["name"]: param["defaultValue"] for param in self.parameters.values()})
            args = [
                "-m", 'run_component',
                "-m", Path(component["entrypoint"]).stem,
                "-p", f"{json_params}",
                "-r", f"{req_list_path}",
            ]

        else:
            # gpuruntime step requires Python environment with onnxruntime installed
            # TODO: check gpuruntime version if needed
            if component["context"] is None:
                shutil.copy(_runner_path / 'gpuruntime_requirements.txt', component["env_dir"] / REQUIREMENTS_TXT)
                self._init_component_venv(component)
                shutil.copy(_runner_path / 'run_gpuruntime_component.py', component["env_dir"])
                shutil.copy(_runner_path.parent / 'model_config_pb2.py', component["env_dir"])

            args = [
                "-m", 'run_gpuruntime_component',
                "-m", component["entrypoint"],
                "-c", "config.pbtxt",
            ]

        args += [
            "-i", input_payload_path.name,
            "-o", output_payload_path.name,
            "-ll", logging.getLevelName(self.log_level)
        ]

        # Run the component in the created Python environment
        executable_path = _relative_to(component['bin_path'] / 'python', component["env_dir"])
        cmd = [f"{executable_path}"] + args
        _logger.info(f"Running command: {subprocess.list2cmdline(cmd)}")
        p = subprocess.Popen(cmd, cwd=component["env_dir"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if p.stdout is not None:
            for line in p.stdout:
                _logger.info(line.strip())
        returncode = p.wait()
        if returncode not in [RETURN_CODE_OK, RETURN_CODE_DEPRECATED]:
            self.cleanup = False
            raise RuntimeError(f"""\
There was an error while running component '{name}'.
You can check the test results in directory '{component['env_dir']}'
""")
        else:
            response_wrapped = True if returncode == RETURN_CODE_DEPRECATED else False

        # Deserialize and validate output payload
        _logger.info(f"Loading output payload from '{output_payload_path}'")
        output_payload = joblib.load(output_payload_path)
        output_payload = output_payload if isinstance(output_payload, list) else [output_payload]
        self.report_writer.set_output_payload_length(name, len(output_payload))
        if response_wrapped:
            output_payload = [json.loads(item['output']) for item in output_payload if item['ready']]
        else:
            output_payload = [output for output in output_payload if output is not None]
        validate_payload(output_payload, component["outputType"], batch_output)

        # Only return the first item if the input was a single item, or None if there are no valid results.
        if result_is_list:
            return output_payload
        return output_payload[0] if len(output_payload) > 0 else None

    def update_parameters(self, parameters: dict):
        """
        Validates and updates pipeline parameters.
        The elements of the dictionary must match the parameters specified in the pipeline configuration package.
        If any of the names or types does not match, all parameters will remain untouched.

        Args:

            parameters (dict): names and values of parameters to update

        Raises:

            AssertionError:
                When:
                - either `name` is not in the configured parameters,
                - or `defaultValue` type is different from the configured one
        """

        for key,value in parameters.items():
            if key not in self.parameters.keys() or self.parameters[key]["type"] != type_map.get(type(value).__name__):
                raise AssertionError(f"Pipeline has no parameters with the name '{key}' and type '{type_map.get(type(value).__name__)}'")

        for key, value in parameters.items():
            self.parameters[key]["defaultValue"] = value

    def run_pipeline(self, payload: Optional[Union[dict, list, DataStream]] = {}) -> Optional[Union[dict, list]]:
        """
        Runs all the components sequentially, assuming the output of a component is only consumed by the next.
        The input data can be a single input record in a dictionary or a batch of input records in a list of dictionaries.
        For each component the supplied input data is saved as `input.joblib` in the component runtime directory,
        and the output is saved as `output.joblib`.

        Args:
            payload (dict or list): One or more input records for the pipeline.

        Returns:
            The output of the last component.
        """

        for name in self.components.keys():
            payload = self.run_component(name, payload)

        return payload

def validate_payload(data: list, variables: list, batch: bool, logger = _logger):
    """
    Validates that data is a valid list of input or output payload items.
    Variables list what variables each playload item has.
    Batch indicates if the payload items are themselves batches of items or not.
    """
    assert isinstance(data, list), "payload data must be a 'list'"
    for i in data:
        if batch:
            assert isinstance(i, list), "batch payload items must be 'list' instances"
        else:
            i = [i]
        for j in i:
            validate_payload_item(j, variables, logger)

def validate_payload_item(data: dict, variables: list, logger):
    """
    Validates that data is a valid payload item.
    Variables listed must have a corresponding field in data.
    The types of the values must match their declared type.
    """
    assert isinstance(data, dict), "payload items must be 'dict' isntances"
    for variable in variables:
        name = variable["name"]

        value = data.get(name, None)
        if value is None:
            logger.warning(f"WARNING! Variable '{name}' is missing from input, output or metric")
            continue

        if variable["type"] == "String":
            assert isinstance(value, str), "'String' value must be an 'str'"

        if variable["type"] == "StringArray":
            assert isinstance(value, list), "'StringArray' value must be a 'list'"
            assert all(isinstance(i, str) for i in value), "'StringArray' items must be 'str' isntances"

        if variable["type"] == "Object":
            assert isinstance(value, dict), "'Object' value must be a 'dict'"
            values = list(value.values())
            assert len(values) == 2, "'Object' value must have exactly 2 items"
            ok = isinstance(values[0], str) and isinstance(values[1], bytes) or isinstance(values[1], str) and isinstance(values[0], bytes)
            assert ok, "'Object' value must have exactly one 'str' and one 'bytes' field"

    payload_names = set(data.keys())
    variable_names = { variable["name"] for variable in variables }
    variable_names.add('timestamp')
    extra_variables = payload_names - variable_names
    if len(extra_variables):
        logger.warning(f"WARNING! These variables are not declared but are part of the payload: {extra_variables}")
