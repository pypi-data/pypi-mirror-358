# Copyright (C) Siemens AG 2025. All Rights Reserved. Confidential.
import json
import logging
import os
from pathlib import Path
import shutil
import subprocess
from typing import Optional, Union
import venv

import joblib
from simaticai.deployment import PythonComponent, GPURuntimeComponent
from simaticai.testing.data_stream import DataStream

PYTHON_RUNNER_PATH = Path(__file__).parent / 'run_component.py'
GPU_RUNNER_PATH = Path(__file__).parent / 'run_gpuruntime_component.py'
GPU_REQUIREMENTS_PATH = Path(__file__).parent / 'gpuruntime_requirements.txt'
GPU_CONFIG_PATH = Path(__file__).parents[1] / 'model_config_pb2.py'

class ComponentRunner():
    """
    Class to run a Pipeline Component in a virtual environment.
    Supported Component Types:
    - PythonComponent
    - GPURuntimeComponent

    Args:
    component: PythonComponent or GPURuntimeComponent
    workdir: Path to the directory where the component should be run. If None, the current working directory is used.
    cleanup: If True, the workdir is deleted after the context manager exits.

    """
    def __init__(self, component, workdir=None, cleanup=False):
        self.component = component
        self.parameters = {}
        self.cleanup = cleanup

        self._logger = self._set_logger()

        self._create_workdir(component, workdir)
        self._copy_resources()
        self._create_venv()
        self._install_requirements()

    def __enter__(self):
        return self
    
    def __exit__(self, exception_type, exception_value, traceback):
        if exception_type is not None:
            self._logger.error(f"Exception occurred: {exception_type.__name__}: {exception_value}")
            return False
        if self.cleanup:
            shutil.rmtree(self.workdir)

    def _set_logger(self):
        """
        Set the logger for the ComponentRunner.
        """
        logger = logging.getLogger(__name__)        
        log_level = os.environ.get("loglevel", "INFO").upper()
        logger.setLevel(log_level)
        handler = logging.StreamHandler()
        handler.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _create_workdir(self, component, workdir):
        """
        Create a workdir for the component.
        """
        if workdir is None:
            self.workdir = Path.cwd() / component.name
        else:
            self.workdir = Path(workdir) / component.name

        self.workdir.mkdir(parents=True, exist_ok=True)        
        self._logger.info(f"Created workdir: {self.workdir}")

    def _copy_resources(self):
        """
        Copy the required resources of the component to the workdir.
        In case of a PythonComponent, also creates the dependencies into requirements.txt.
        In case of a GPURuntimeComponent, also creates a requirements.txt with the required onnx and onnxruntime dependencies.
        Also adds the runner script to the workdir.
        In case of the source folder same as the workdir, the resources are not copied, 
        so any changes in source will affect the workdir.
        """
        if isinstance(self.component, PythonComponent):
            same_resources = []
            for from_path in self.component.resources.keys():
                try:
                    to_path = self.workdir / self.component.resources[from_path]
                    shutil.copy(from_path, to_path)
                except shutil.SameFileError:
                    same_resources.append(from_path.name)
            if same_resources:
                self._logger.info("Resources are already in workdir, which are not copied:")
                for resource in same_resources:
                    self._logger.debug(f"  - {resource}")
            self.component.python_dependencies.save(self.workdir)  # saves manually added Python packages and requirements.txt
            shutil.copy(PYTHON_RUNNER_PATH, self.workdir)
        else:
            model_dir = Path(self.workdir / "1")
            model_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(self.component.model_path, model_dir / "model.onnx")
            Path(self.workdir / "config.pbtxt").write_text(f"{self.component.auto_config}")

            shutil.copy(GPU_RUNNER_PATH, self.workdir / "run_component.py")
            shutil.copy(GPU_REQUIREMENTS_PATH, self.workdir / "requirements.txt")
            shutil.copy(GPU_CONFIG_PATH, self.workdir)
        
        self._logger.info("Resources are copied into the workdir.")

    def _create_venv(self):
        """
        Create a Python virtual environment in the workdir.
        The created virtual environment is stored in the context_dir and 
        has the same version as the current Python interpreter.
        """
        context_dir = self.workdir / ".venv"
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(context_dir)

        self.context_dir = builder.ensure_directories(context_dir)
        self.bin_path = Path(self.context_dir.bin_path).resolve()
        
        self._logger.info(f"Python virtualenv created in folder '{self.bin_path.parent}'")
    
    def _install_requirements(self):
        """
        Installs the required Python dependencies.
        """
        # TODO: Add log_module install
        # TODO: Add install from PythonPackages.zip
        cmd = [str(self.bin_path / 'pip'), 'install', 'joblib', '-r', 'requirements.txt']
        result = subprocess.run(cmd, cwd=self.workdir, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.decode())

        result_lines = result.stdout.decode().split("\n")
        installed_message = " ".join([line for line in result_lines if "Successfully installed" in line])
        self._logger.info(installed_message)

    def set_parameters(self, parameter_name, parameter_value):
        """
        Set the parameters for the component.
        """
        self.parameters[parameter_name] = parameter_value

    def run(self, input_payload: Optional[Union[dict, list]]) -> Optional[Union[dict, list]]:
        """
        Run the component with the input payload.

        Parameters:
        input_payload: Input payload for the component.

        Returns:
        Output payload from the component.

        Side Effects:
        - The input payload is saved in the workdir.
        - The output payload is loaded from the workdir.
        """
        input_payload_path: Path  = self.workdir / "input.joblib"
        output_payload_path: Path = self.workdir / "output.joblib"

        batch_input: bool  = self.component.batch.inputBatch
        if isinstance(input_payload, DataStream):
            input_payload = [item for item in input_payload]
        elif isinstance(input_payload, dict):
            input_payload = [input_payload]

        input_variables = [{'name': name, 'type': input['type']} for name, input in self.component.inputs.items()]
        self._validate_payload(input_payload, input_variables, batch_input)

        joblib.dump(input_payload, input_payload_path)

        cmd = self._create_command(input_payload_path, output_payload_path)
        
        self._logger.info("Running command: " + " ".join(cmd))

        result = subprocess.run(cmd, cwd=self.workdir, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.decode())
        
        self._logger.debug(result.stderr.decode())
        output_payload = joblib.load(output_payload_path)

        batch_output: bool = self.component.batch.outputBatch
        output_payload = output_payload if isinstance(output_payload, list) else [output_payload]
        output_payload = [output for output in output_payload if output is not None]
        output_variables = [{'name': name, 'type': output['type']} for name, output in self.component.outputs.items()]
        if isinstance(self.component, PythonComponent):
            output_variables += [{'name': name} for name in self.component.metrics]
        self._validate_payload(output_payload, output_variables, batch_output)

        return output_payload

    def _check_instance(self, element, element_name: str, instance):
        if not isinstance(element, instance):
            self._logger.error(f"{element_name} must be an instance of {instance.__name__}")
            raise ValueError(f"{element_name} must be an instance of {instance.__name__}")

    def _check_variable_types(self, variable: dict, value):
        if variable["type"] == "String":
            self._check_instance(value, "String value", str)

        if variable["type"] == "StringArray":
            self._check_instance(value, "StringArray value", list)
            for i in value:
                self._check_instance(i, "StringArray item", str)

        if variable["type"] == "Object":
            self._check_instance(value, "Object value", dict)
            values = list(value.values())
            if len(values) != 2:
                self._logger.error("Object value must have exactly 2 items")
                raise ValueError("Object value must have exactly 2 items")
            ok = isinstance(values[0], str) and isinstance(values[1], bytes) or isinstance(values[1], str) and isinstance(values[0], bytes)
            if not ok:
                self._logger.error("Object value must have exactly one 'str' and one 'bytes' field")
                raise ValueError("Object value must have exactly one 'str' and one 'bytes' field")
    
    def _validate_payload(self, payload: list, variables: list, batch: bool):
        self._check_instance(payload, "Payload", list)
        for payload_element in payload:
            if batch:
                self._check_instance(payload_element, "Batch payload element", list)
            else:
                payload_element = [payload_element]

            for item in payload_element:
                self._validate_payload_item(item, variables)

    def _validate_payload_item(self, item: dict, variables: list):
        self._check_instance(item, "Payload item", dict)
        for variable in variables:
            name = variable["name"]
            value = item.get(name, None)
            if value is None:
                self._logger.warning(f"WARNING! Variable '{name}' is missing from input, output or metric")
                continue

            self._check_variable_types(variable, value)

        payload_names = set(item.keys())
        variable_names = { variable["name"] for variable in variables }
        variable_names.add('timestamp')
        extra_variables = payload_names - variable_names
        if len(extra_variables):
            self._logger.warning(f"WARNING! These variables are not declared but are part of the payload: {extra_variables}")

    def _create_command(self, input_payload_path, output_payload_path):
        """
        Create the command to run the component.
        
        """
        cmd = [str(self.bin_path / 'python'), "-m", 'run_component']
        if isinstance(self.component, PythonComponent):
            cmd += [
                "-m", Path(self.component.entrypoint).stem,
                "-p", json.dumps(self.parameters)
            ]
        if isinstance(self.component, GPURuntimeComponent):
            # TODO: check relative path to run_component.py
            model_path = Path(self.workdir / "1" / "model.onnx").absolute().resolve()
            config_path = Path(self.workdir / "config.pbtxt").absolute().resolve()
            cmd += [
                "-m", str(model_path),
                "-c", str(config_path),
            ]

        cmd += [
            "-i", input_payload_path.name,
            "-o", output_payload_path.name,
            "-ll", logging.getLevelName(self._logger.getEffectiveLevel())
        ]                
        return cmd
