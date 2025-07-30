# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

"""
Packaging ML models for deployment on the AI Inference Server.

The AI SDK offers the functionality to create a pipeline configuration package and wrap trained models, which can be converted to an
edge configuration package and then uploaded and run on an AI Inference Server on an Industrial Edge device.

From a deployment perspective, the inference pipeline can consist of one or more components. This is independent of the logical structure of
the inference pipeline. For example, a typical time series pipeline that consists of multiple Scikit Learn pipeline elements can be packaged
into a single pipeline component, which includes both a feature extractor and a classifier. Alternatively, you can deploy the same pipeline
split into two components, one for the feature extractor and another for the classifier.

To keep things simple and less error-prone, a pipeline should have as few components as possible.
In many cases, a single component will be sufficient.
However, there might be reasons why you might consider using separate components, such as:

- You need a different Python environment for different parts of your processing, e.g., you have components requiring conflicting package versions.
- You want to exploit parallelism between components without implementing multithreading.
- You want to modularize and build your pipeline from a pool of component variants, which you can combine flexibly.

The AI SDK allows you to create pipeline components implemented in Python and compose linear pipelines of one or multiple of such components.
The API is designed to anticipate future possible types of components that might be based on a different technology than Python, e.g. ONNX or
native TensorFlow Serving. Currently, only Python is supported.

For a comprehensive overview on how to package ML models in the context of a machine learning workflow, we recommend you refer to
the AI SDK User Manual, especially the chapter concerning packaging models into an inference pipeline. We also recommend you
follow the project templates for the AI SDK, which provide packaging notebooks as examples, and where source code and
saved trained models are organized into a given folder structure.

"""

from dataclasses import dataclass
import json
import logging
import math
import os
import uuid
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime
from importlib import resources as module_resources
from pathlib import Path, PurePath
from typing import Optional, Tuple, Union

import jsonschema
import jsonschema.exceptions
import pkg_resources
import yaml
from MarkupPy import markup
from google.protobuf import text_format

from simaticai import model_config_pb2
from simaticai.helpers import pep508, tempfiles, yaml_helper, model_config, calc_sha
from simaticai.helpers.tempfiles import OpenZipInTemp
from simaticai.packaging.constants import (
    PIPELINE_CONFIG, RUNTIME_CONFIG, DATALINK_METADATA,  # pipeline configuration files
    TELEMETRY_YAML, README_HTML,  # additional pipeline information files
    REQUIREMENTS_TXT, PYTHON_PACKAGES_ZIP,  # component dependency configuration
    PYTHON_PACKAGES, supported_types, MSG_NOT_FOUND,  # additional constants
    PIPELINE_SIZE_LIMIT
)

from simaticai.packaging.python_dependencies import PythonDependencies
from simaticai.packaging.wheelhouse import create_wheelhouse

from simaticai.helpers.reporter import PipelineReportWriter, ReportWriterHandler
from simaticai.packaging.python_dependencies import _logger as _python_dependencies_logger
from simaticai.packaging.wheelhouse import _logger as _wheelhouse_logger

logging.basicConfig()
logging.getLogger().handlers = [logging.StreamHandler(sys.stdout)]
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

_version_matcher = re.compile('Version: ([^ ]+).*')
_transitive_matcher = re.compile('Requires: (.+)')


def find_dependencies(name: str, dependencies: dict):
    """
    @Deprecated, reason: uses 'pip show' which only works for installed packages on the current platform.

    Collects all dependencies of the Python module given with its `name` in the current Python environment.

    All inherited dependencies will be added to the `dependencies` dictionary with the installed version of the module.
    The method executes an OS command like `python -m pip show scikit-learn`.

    Args:
        name (str): Name of the Python module to be searched through for its dependencies.
        dependencies (dict): Dictionary to collect the dependencies with the module name as key, and the installed version as value.

    Returns:
        dict: The `dependencies` dictionary with the collected module names and versions.
    """

    cmd_line = [sys.executable, '-m', 'pip', 'show', name]
    result = subprocess.run(cmd_line, stdout=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print(f"Dependency {name} is not found and cannot be added.")
        return dependencies

    version = None
    for line in result.stdout.splitlines():

        version_matches = _version_matcher.match(line)
        if version_matches:
            version = version_matches.groups()[0].strip()

        transitive_matches = _transitive_matcher.match(line)
        if transitive_matches:
            transitives = transitive_matches.groups()[0].split(", ")
            for dependency in transitives:
                if dependency not in dependencies:
                    find_dependencies(dependency, dependencies)

    if name not in dependencies:
        spec = pep508.Spec(name, [], [('==', version)] if version else [], None)
        dependencies[name] = spec
        print("Found:", spec)
    return dependencies


def python_version_validator(version: str):
    """
    Checks if Python version string is valid and describes supported version.

    Only version 3.10 and 3.11 is supported. A patch version is optional and accepted but logs a warning.

    Accepted syntaxes are:

        - {major}.{minor}
        - {major}.{minor}.{patch}

    Args:
        version (str): Python version string

    Raises:
        ValueError: if the provided version is not supported
    """

    supported_versions = ["3.10", "3.11"]

    error_message = "The defined python version is not supported. Currently supported Python versions are 3.10 and 3.11. Python version must be specified only with major and minor version, e.g. '3.10'."

    warning_message = """Required Python version was specified with patch version.
                Please note that the patch digit of the required Python version is often not taken into account by the Python ecosystem,
                so there is no guarantee it has the desired effect."""

    python_version_matcher = re.match(r'^(3)\.(0|[1-9][0-9]*)\.?(0|[1-9][0-9]*)?$', str(version))

    major_minor_version = "0.0"
    has_patch_version = False

    if python_version_matcher is not None:
        major_minor_version = f"{python_version_matcher.group(1)}.{python_version_matcher.group(2)}"
        has_patch_version = python_version_matcher.group(3) is not None

    if major_minor_version not in supported_versions:
        raise ValueError(error_message)

    if has_patch_version:
        _logger.warning(warning_message)


class Component:
    """
    Base class for pipeline components, with name, description, and a list of inputs and outputs.

    A new component is created with the given name and an empty input and output list.

    Args:
        name (str): Name of the component
        desc (str): Optional description of the component
        inputs (dict): Dictionary of (name, type) pairs, which describe the input variables
        outputs (dict): Dictionary of (name, type) pairs, which describe the output variables
    """
    reserved_names = ["timestamp"]

    @dataclass
    class BatchInfo:
        """
        Batch information for the component.

        This attribute specifies whether the component can handle batch input or output data.
        When set to True, the component will receive data in the form of a list of dictionaries instead of a single dictionary.
        It is important to note that the input and output variables on the component should still be defined as if they are single variables.

        If the input of the pipeline is configured for batch processing, it is recommended not to configure timeshifting, as the list will have the same timestamp for all elements, potentially resulting in data loss.
        """
        inputBatch: bool = False
        outputBatch: bool = False

        def dict(self):
            return {
                'inputBatch': 'Yes' if self.inputBatch is True else 'No',
                'outputBatch': 'Yes' if self.outputBatch is True else 'No'
            }

    def __init__(self, name: str, desc: str = ""):
        """
        Creates a new component with the given name and an empty input and output list.

        Args:
            name (str): Name of the component.
            desc (str): Optional description of the component
        """

        self.name = name
        self.desc = desc
        self.inputs = {}
        self.outputs = {}

        self.batch = self.BatchInfo(False, False)

    def __repr__(self) -> str:
        text = f"[{self.__class__.__name__}] {self.name}\n"
        if self.desc != "":
            text += f"{self.desc}\n"
        if len(self.inputs) > 0:
            text += "\nComponent Inputs:\n"
            for name, input in self.inputs.items():
                text += f"> {name} ({input['type']}){': ' + input['desc'] if input.get('desc') is not None else ''}\n"
        if len(self.outputs) > 0:
            text += "\nComponent Outputs:\n"
            for name, output in self.outputs.items():
                text += f"< {name} ({output['type']}){': ' + output['desc'] if output.get('desc') is not None else ''}\n"
        return text

    def add_input(self, name: str, _type: str, desc: Optional[str] = None):
        """
        Adds a new input to the component with its type.
        Name of the variables cannot be reserved name like 'timestamp'.
        Input variable 'timestamp' is a prebuilt key in the payload and its value contains the timestamp when the payload is created by AI Inference Server.

        Types supported by AI Inference Server version 1.6 are contained in the `type_dictionary`. Newer AI Inference server version may support additional types.
        In case the type is not known by the AI SDK, a warning message will be printed.
        The most frequently used types are
        - String:
            Typically used for data received from Databus
        - Object:
            Object type variables are designed to receive from Vision Connect or transfer images between components
        - Numeric scalar types:
            Typically used for data received from S7 Connector

        The example payload below shows the format of image received from VCA Connector
        ```python
            payload = { "image":
                {
                    "resolutionWidth": image.width,
                    "resolutionHeight": image.height,
                    "mimeType": ["image/raw"],
                    "dataType": "uint8",
                    "channelsPerPixel": 3,
                    "image": _swap_bytes(image.tobytes())
                }
            }
        ```
        Between components the format is the same format as the format of Object as an output.
        ```python
            "processedImage": {
                "metadata": json.dumps( {
                                "resolutionWidth": image.width,
                                "resolutionHeight": image.height
                                }
                            ),
                "bytes": image.tobytes()
            }
        ```

        Args:
            name (str): Name of the new input.
            _type (str): Type of the new input.
            desc (str): Description of the input. (optional)
        """
        if self.inputs is None:
            self.inputs = {}
        if name in self.inputs:
            raise AssertionError(f"Input '{name}' already exists.")
        if name.lower() in self.reserved_names:
            raise AssertionError(f"Input '{name}' is a reserved keyword.")

        if _type not in supported_types:
            _logger.warning(f"WARNING! Unknown type '{_type}' for input variable '{name}'. Please check if the target Inference Server supports this type.")

        self.inputs[name] = {
            "type": _type,
        }
        if desc is not None:
            self.inputs[name]['desc'] = desc

    def change_input(self, name: str, _type: str, desc: Optional[str] = None):
        """
        Changes one of the inputs of the component.

        Args:
            name (str): Name of the input to be changed.
            _type (str): New type of the input.
            desc (str): Description of the input. (optional)
        """
        if name not in self.inputs:
            raise AssertionError(f"There is no input with name '{name}'")
        if _type not in supported_types:
            _logger.warning(f"WARNING! Unknown type '{_type}' for input variable '{name}'. Please check if the target Inference Server supports this type.")
        self.inputs[name]['type'] = _type
        if desc is not None:
            self.inputs[name]['desc'] = desc

    def delete_input(self, name: str):
        """
        Deletes an input from the component by name.
        Once the package has been created with the given component, it is recommended not to change the component directly.
        Instead, all necessary methods to change it are available through the package to avoid component inconsistencies.
        It is recommended to use `package.delete_input_wire(...)` with default parameter `with_input=True`.

        Args:
            name (str): Name of the input to be deleted.
        """
        if name not in self.inputs:
            raise AssertionError(f"Component '{self.name}' has no input '{name}'")
        self.inputs.pop(name)

    def add_output(self, name: str, _type: str, desc: Optional[str] = None):
        """
        Adds a new output to the component.

        Types supported by AI Inference Server version 1.6 are contained in the `type_dictionary`. Newer AI Inference server version may support additional types.
        In case the type is not known by the AI SDK, a warning message will be printed.
        The most frequently used types are
        - String:
            Typically used for data to be sent to Databus
        - Object:
            Typically used for images to be sent to ZMQ Connector
        - Numeric scalar types:
            Typically used for data sent to S7 Connector

        For outputs of type `Object` the entrypoint must return with a `dictionary` containing two fields, where one field has type `str` and the other field has type `bytes`.
        The example below shows the required format, assuming that 'image' is a PIL Image.
        ```python
            "processedImage": {
                "metadata": json.dumps( {
                                "resolutionWidth": image.width,
                                "resolutionHeight": image.height
                                }
                            ),
                "bytes": image.tobytes()
            }
        ```

        Args:
            name (str): Name of the new output.
            _type (str): Type of the new output.
            desc (str): Description of the output. (optional)
        """
        if self.outputs is None:
            self.outputs = {}
        if name in self.outputs:
            raise AssertionError(f"Output '{name}' already exists")
        if name.lower() in self.reserved_names:
            raise AssertionError(f"Output '{name}' is a reserved keyword.")
        if _type not in supported_types:
            _logger.warning(f"WARNING! Unknown type '{_type}' for input variable '{name}'. Please check if the target Inference Server supports this type.")
        self.outputs[name] = {
            "type": _type,
        }
        if desc is not None:
            self.outputs[name]['desc'] = desc

    def change_output(self, name: str, _type: str, desc: Optional[str] = None):
        """
        Changes one of the outputs of the component.

        Args:
            name (str): Name of the output to be changed.
            _type (str): The new type of the output.
            desc (str): Description of the output. (optional)
        """
        if name not in self.outputs:
            raise AssertionError(f"There is no output with name '{name}'")
        if _type not in supported_types:
            _logger.warning(f"WARNING! Unknown type '{_type}' for input variable '{name}'. Please check if the target Inference Server supports this type.")
        self.outputs[name]['type'] = _type
        if desc is not None:
            self.inputs[name]['desc'] = desc

    def delete_output(self, name: str):
        """
        Deletes an output from the component by name.
        Once the package has been created with the given component, it is recommended not to change the component directly.
        Instead, all necessary methods to change it are available through the package to avoid component inconsistencies.
        Deleting an output which is represented in any wire will cause package inconsistency.

        Args:
            name (str): Name of the output to be deleted.
        """
        if name not in self.outputs:
            raise AssertionError(f"Component '{self.name}' has no output '{name}'")
        self.outputs.pop(name)

    def _to_dict(self):
        inputs = []
        inputs += [{
            'name': name,
            'type': self.inputs[name]['type'],
        } for name in self.inputs]

        outputs = []
        outputs += [{
            'name': name,
            'type': self.outputs[name]['type'],
            'metric': False,
        } for name in self.outputs]

        return {
            'name': self.name,
            'description': self.desc,
            'batch': self.batch.dict(),
            'inputType': inputs,
            'outputType': outputs,
        }

    def validate(self):
        """
        Empty method for child classess to implement.
        """
        pass

    def save(self, destination, validate):
        """
        Empty method for child classess to implement.
        """
        pass


class PythonComponent(Component):
    """
    A pipeline component implemented using Python scripts and libraries.

    A `PythonComponent` wraps Python code resource files such as saved models into a structured folder, which can be added to a pipeline
    configuration package.

    For a comprehensive overview on how to wrap ML models into Python components, we recommend you refer to
    the AI SDK User Manual, especially the guideline for writing pipeline components. We also recommend you
    study the example Python components in the E2E Tutorials for the AI SDK.

    A new `PythonComponent` is empty.

    Args:
        name (str): Component name. (default: inference)
        desc (str): Component description (optional)
        version (str): Component version. (default: 0.0.1)
        python_version (str): Python version on the target AI Inference Server.
            At the moment of writing, the current version supports Python 3.10 and 3.11.
    """

    def __init__(self, name="inference", version="0.0.1", python_version='3.10', desc: str = ""):
        """
        Creates a new, empty Python component.

        Args:
            name (str): Component name. (default: inference)
            desc (str): Component description (optional)
            version (str): Component version. (default: 0.0.1)
            python_version (str): Python version on the target AI Inference Server. At the moment of writing, AI Inference Server supports Python 3.10 and 3.11.
        """

        super().__init__(name=name, desc=desc)

        try:
            python_version_validator(python_version)
        except ValueError as error:
            raise AssertionError(error)

        self.python_version = python_version
        self.version = version
        self.metrics = {}
        self.entrypoint: Optional[Path] = None
        self.resources = {}
        self.python_dependencies = PythonDependencies(python_version)
        self._replicas = 1
        self.is_valid = False

    def __repr__(self) -> str:
        text = super().__repr__()

        if len(self.metrics) > 0:
            text += "\nMetrics:\n"
            for name, metric in self.metrics.items():
                text += f"< {name}{': ' + metric['desc'] if metric.get('desc') is not None else ''}\n"

        if len(self.resources):
            text += "\nResources:\n"
            for path, base in self.resources.items():
                text += f"  {base}/{path.name}\n".replace('./', '')

        if self.entrypoint is not None:
            text += f"Entrypoint: {self.entrypoint}\n"

        return text

    def set_entrypoint(self, entrypoint: str):
        """
        Sets the entrypoint module for the component.

        The entrypoint is the Python code which is responsible for receiving the input data and producing a structured response with the output for the AI Inference Server.
        The script should consume a JSON string and produce another. See the short example below.

        The file will be copied into the root directory of the component on the AI Inference Server, so every file reference should be aligned.

        The example code below shows a basic structure of the entrypoint Python code.
        ```python
        import json
        import sys
        from pathlib import Path

        # by adding the parent folder of your modules to system path makes them available for relative import
        sys.path.insert(0, str(Path('./src').resolve()))
        from my_module import processor  # then the processor module can be imported

        def run(data: str):
            input_data = json.loads(data)  # incoming JSON string is loaded as a dictionary

            result = processor.process_data(input_data)  # the process_data can be called to process the incoming data

            # the code below creates the formatted output for the AI Inference Server
            if result is None:
                answer = {"ready": False, "output": None}
            else:
                answer = {"ready": True, "output": json.dumps(result)}

            return answer
        ```

        Args:
            entrypoint (str): Name of the new entrypoint script to be copied

        """
        self.is_valid = False

        if not any(key.name for key, value in self.resources.items() if key.name == entrypoint and value == '.'):
            raise AssertionError("Entrypoint must be added as resource to the root directory before setting up as entrypoint.")

        self.entrypoint = Path(entrypoint)

    def add_resources(self, base_dir: os.PathLike, resources: Union[os.PathLike, list]):
        """
        Adds files to a component.

        To make your file resources available on the AI Inference Server you need to add them to the package resources.
        These resources can be Python or config files, serialized ML models or reference data.
        They are then available on path {component_root}/{resources} in the runtime environment.
        When saving the package they will be copied from {base_dir}/{resources} into the package.
        Files in '__pycache__' folders will be excluded.  
        Until version 2.3.0 of AI SDK hidden files and folders (starting with '.') are also excluded.

        Args:
            base_dir (path-like): Root folder of your code from which the resources are referred
            resources (os.PathLike or List): A single path or list of relative paths to resource files

        """
        self.is_valid = False

        base_dir = Path(base_dir).resolve().absolute()
        if not base_dir.is_dir():
            raise AssertionError(f"Parameter 'base_dir' must be a directory and available in path {base_dir}.")
        resources = resources if type(resources) is list else [resources]

        for resource in resources:
            self._add_resource(base_dir, resource)

    def _add_resource(self, base_dir: Path, resource: os.PathLike):
        self.is_valid = False
        if Path(resource).is_absolute() or '..' in resource:
            raise AssertionError("The resource path must be relative and cannot contain '/../' elements.")

        resource_path = base_dir / resource

        if resource_path.is_file():
            self._add_resource_file(base_dir, resource_path)
            return

        if resource_path.is_dir():
            for glob_path in resource_path.rglob("*"):
                if glob_path.is_file():
                    self._add_resource_file(base_dir, glob_path)
            return

        raise AssertionError(f"Specified resource is not a file or directory: '{resource}'")

    def _add_resource_file(self, base_dir: Path, resource_path: Path):
        self.is_valid = False
        for parent in resource_path.parents:
            if parent.name == '__pycache__':
                return

        if resource_path in self.resources.keys():
            _logger.warning(f"Resource '{resource_path}' is already added to target directory '{self.resources[resource_path]}'")
            return

        self.resources[resource_path] = f"{resource_path.parent.relative_to(base_dir)}"

    def add_dependencies(self, packages: list):
        """
        Adds required dependencies for the Python code.

        The list must contain the name of the Python packages or tuples in the form of (name, version) which are required to execute the component on AI Inference Server.
        The method will search for the packages for the target platform and collect their transitive dependencies as well.
        Packages that are distributed only in source format can be added too, but only if they are pure Python packages.

        Args:
            packages (list): Can be a list of strings (name) or a list of tuples (name, version) of the required packages for component execution
        """
        self.is_valid = False
        self.python_dependencies.add_dependencies(packages)

    def set_requirements(self, requirements_path: os.PathLike):
        """
        Reads the defined dependencies from the given `requirements.txt` file and creates a new dependency list. Previously added dependencies will be cleared.

        The file format must follow Python's requirements file format defined in PEP 508.
        It can contain URLs to additional repositories in the form of `--extra-index-url=my.repo.example.com`.

        Args:
            requirements_path (str): Path of the given `requirements.txt` file
        """
        self.is_valid = False
        self.python_dependencies.set_requirements(requirements_path)

    def add_python_packages(self, path: str) -> None:
        """
        Adds Python package(s) to the `PythonPackages.zip` file of the component.

        The `path` parameter can refer to either a `whl`, a `zip` or a `tar.gz` file.
        Zip files can be either a source distribution package or a collection of Python packages. Only pure Python source distributions are allowed.
        The dependency list of the component will be extended with the files added here, so that they will also get installed on the AI Inference Server.
        The method uses the `tempfile.tempdir` folder, so make sure that the folder is writeable.

        The wheel files must fulfill the requirements of the targeted device environment
        (e.g., the Python version must match the supported Python version of the targeted AI Inference Server, and the platform should be one of the supported ones too).

        Args:
            path (str): Path of the distribution file

        Examples:
            `component.add_python_packages('../resources/my_package-0.0.1-py3-none-any.wheel')`
                adds the wheel file to `PythonPackages.zip` and adds dictionary item `component.dependencies['my_package'] = '0.0.1'`

            `component.add_python_packages('../resources/inference-wheels.zip')`
                adds all the wheel files in the zip to `PythonPackages.zip` and `component.dependencies`
        """
        self.is_valid = False
        self.python_dependencies.add_python_packages(path)

    def set_parallel_steps(self, replicas):
        """
        Sets the number of parallel executors.

        This method configures how many instances of the component can be
        executed at the same time.
        The component must be suitable for parallel execution. The inputs arriving
        to the component will be processed by different instances in parallel,
        and these instances do not share their state (e.g. variables). Every
        instance is initialized separately and receives only a fraction of the inputs.
        AI Inference Server supports at most 8 parallel instances.```

        Args:
            replicas (int): Number of parallel executors. Default is 1.

        Raises:
            ValueError: if the given argument is not a positive integer.
        """
        self.is_valid = False
        if (not isinstance(replicas, int)) or replicas < 1:
            raise ValueError("Replica count must be a positive integer.")
        if 8 < replicas:
            _logger.warning("The current maximum of parallel executors is 8.")
        self._replicas = replicas

    def add_metric(self, name: str, desc: Optional[str] = None):
        """
        Adds a metric that will be automatically used as a pipeline output.

        Args:
            name (str): Name of the metric.
            desc (str): Description of the metric. (optional)
        """
        if "_" not in name:
            raise AssertionError("The metric name must contain at least one underscore")
        if self.metrics is None:
            self.metrics = {}
        if name in self.metrics:
            raise AssertionError(f"Metric '{name}' already exists")
        self.metrics[name] = {}
        if desc is not None:
            self.metrics[name]['desc'] = desc

    def delete_metric(self, name: str):
        """
        Remove a previously added metric.

        Args:
            name (str): Name of the metric to be deleted.
        """
        if name not in self.metrics:
            raise AssertionError(f"Component '{self.name}' has no metric '{name}'")
        self.metrics.pop(name)

    def _to_dict(self):
        component_dict = {
            **super()._to_dict(),
            'version': self.version,
            'entrypoint': f"./{self.entrypoint.name}",
            'hwType': 'CPU',
            'runtime': {
                'type': 'python',
                'version': self.python_version
            },
            'replicas': self._replicas
        }

        component_dict["outputType"] += [{
            'name': name,
            'type': 'String',
            'metric': True,
        } for name in self.metrics.keys()]

        return component_dict

    def enable_dependency_optimization(self):
        """
        Allows changing repository URLs to optimize the package size

        Allows the replacement of the `--index-url` argument during `pip download` to download
        CPU runtime optimized dependencies only. Enabling this optimization, the present
        `--index-url` will be prepended to the `--extra-index-url` list, and the Pytorch CPU only repository
        will be set as the `--index-url`.
        A warning message will be printed if the repository URL modification was necessary.
        Some dependencies have both CPU and GPU runtime
        versions, pytorch for example, but a `PythonComponent` can only run on CPU, so
        packaging the additional GPU runtime dependencies just enlarges the package size.
        If you want to run your model on GPU, convert it to an `ONNX` model and use it within a
        `GPURuntimeComponent`.
        """
        self.python_dependencies.enable_dependency_optimization()

    def disable_dependency_optimization(self):
        """
        Disables any modification to repository URLs

        Disables the replacement of the `--index-url` argument during `pip download`.
        This way all `--index-url` or `--extra-index-url` arguments will be preserved if they
        were present in the requirements.txt file.
        Some dependencies have both CPU and GPU runtime
        versions, pytorch for example, but a `PythonComponent` can only run on CPU, so
        packaging the additional GPU runtime dependencies just enlarges the package size.
        A warning message will be printed about the package size if this optimization is disabled and
        the dependency list contains GPU optimized dependencies.
        Disabling this optimization will not allow the component to run on GPU.
        If you want to run your model on GPU, convert it to an `ONNX` model and use it within a
        `GPURuntimeComponent`.
        """
        self.python_dependencies.disable_dependency_optimization()

    def validate(self):
        """
        Validates that the component is ready to be serialized and packaged as part of a pipeline.
        """
        if not self.is_valid:
            if self.entrypoint is None:
                raise AssertionError("Entrypoint must be defined")
            if not any(key.name for key, value in self.resources.items() if key.name == self.entrypoint.name and value == '.'):
                raise AssertionError("Entrypoint must be added as resource to the root directory before setting up as entrypoint.")

            if len(self.python_dependencies.dependencies) < 1:
                _logger.warning(f"WARNING! There are no dependencies defined for component '{self.name}'. Please make sure that all necessary dependencies have been added.")

            self.python_dependencies.validate()

            self.is_valid = True

        _logger.info(f"Component '{self.name}' is valid and ready to use.")

    def save(self, destination, validate=True):
        """
        Saves the component to a folder structure, so it can be used as part of a pipeline configuration package.
        Validation can be skipped by setting parameter `validate` to False.
        This is useful when the component is already validated and only intended to be saved.

        The component folder contains the following:

        - `requirements.txt` with a list of Python dependencies
        - Entry point script defined by the `entrypoint` attribute of the component
        - Extra files as added to the specified folders
        - `PythonPackages.zip` with the wheel binaries for the environment to be installed

        Args:
            destination (path-like): Target directory to which the component will be saved.
            validate (bool): With value True, triggers component validation. Defaults to True.
        """
        if validate:
            self.validate()

        folder_path = Path(destination) / self.name
        folder_path.mkdir(parents=True, exist_ok=True)

        for file_path in self.resources:
            dir_path = folder_path / self.resources[file_path]
            os.makedirs(dir_path, exist_ok=True)
            shutil.copy(file_path, dir_path / file_path.name)

        self.python_dependencies.save(folder_path)


class Pipeline:
    """
    `Pipeline` represents a pipeline configuration package with `Components` and wires to provide a data flow on the AI Inference Server.
    The `Components` have inputs and outputs to transfer data to each other and the wires describe this data flow between them.
    The package also contains configuration files required to deploy a pipeline on an Industrial Edge device.

    A newly initialized `Pipeline` does not contain any `Component` or wire, only its name and version will be set.
    The name and version together will define the name of the zip file when the package is saved.

    Args:
        name (str): Name of the package
        version (str): Version of the package
    """
    _wire_hash_string = "{}.{} -> {}.{}"

    def __init__(self, name: str, version: Optional[str] = None, desc: str = ""):
        """
        A newly initialized `Pipeline` will contain no `Component` or wire, just its name and version will be set.
        The name and version will define together the name of the zip file when the package is saved.

        Args:
            name (str): Name of the package
            desc (str): Package description (optional)
            version (str): Version of the package
        """

        self.name = name
        self.desc = desc
        self.version = version
        self.package_id: Optional[uuid.UUID] = None
        self.save_version = None
        self.save_package_id: Optional[uuid.UUID] = None

        self.author = 'AI SDK'

        self.components = {}
        self.wiring = {}
        self.parameters = {}

        self.periodicity = None
        self.timeshift_reference = []

        self.inputs = []
        self.outputs = []
        self.log_level = logging.INFO

        self.report_writer = PipelineReportWriter()
        report_writer_handler = ReportWriterHandler(self.report_writer)
        _logger.addHandler(report_writer_handler)
        _python_dependencies_logger.addHandler(report_writer_handler)
        _wheelhouse_logger.addHandler(report_writer_handler)

    def _set_log_level(self, log_level: int):
        self.log_level = log_level
        _logger.setLevel(self.log_level)

    @staticmethod
    def from_components(components: list, name: str, version: Optional[str] = None, desc: str = "") -> "Pipeline":
        """
        Creates a pipeline configuration from the given components.
        The components are linked in a linear sequence with inputs and outputs auto-wired based on the name of the inputs and outputs of the components.
        The inputs of the first component will be wired as the pipeline inputs and the outputs of the last component will be wired as the pipeline outputs.
        The components must have unique names. Two or more versions of the same component can not be packaged simultaneously without renaming them.

        Args:
            components (list): List of PythonComponents
            name (str): Name of the pipeline
            version (str): Version information of the pipeline. (Optional)
        Returns:
            Pipeline: Pipeline object with the auto-wired components
        """
        pipeline = Pipeline(name, version, desc=desc)

        first_component = components[0]
        pipeline.add_component(first_component)
        pipeline.inputs = [(first_component.name, component_input) for component_input in first_component.inputs]
        pipeline.outputs = [(first_component.name, output) for output in first_component.outputs]

        for component in components[1:]:
            pipeline.add_component(component)
            for (wire_component, wire_name) in pipeline.outputs:
                try:
                    pipeline.add_wiring(wire_component, wire_name, component.name, wire_name)
                except Exception as e:
                    _logger.warning(f"Output variable {wire_component}.{wire_name} couldn't be auto-wired.\nCause: {e}")

            unwired_variables = [f'{component.name}.{x}' for x in component.inputs if not any(s.endswith(f'{component.name}.{x}') for s in pipeline.wiring)]
            if len(unwired_variables) > 0:
                for variable in unwired_variables:
                    _logger.warning(f"Input variable {variable} couldn't be auto-wired.\n")
            pipeline.outputs = [(component.name, output) for output in component.outputs]

        return pipeline

    def __repr__(self) -> str:
        """
        Textual representation of the configured package.
        The method shows the `Components` with their inputs, outputs and parameters as well as the wiring between these `Components`.

        Returns:
            [str]: Textual representation of the package
        """

        text = f"[{self.__class__.__name__}] {self.name} ({self.version})\n"
        if self.desc != "":
            text += f"{self.desc}\n"

        if len(self.parameters) > 0:
            text += "\nPipeline Parameters:\n"
            for name, parameter in self.parameters.items():
                text += f"- {name} ({parameter['type']}, default: '{parameter['defaultValue']}'){(': ' + parameter['desc']) if parameter.get('desc') is not None else ''}\n"

        if len(self.inputs) > 0:
            text += "\nPipeline Inputs:\n"
            for component, name in self.inputs:
                input = self.components[component].inputs[name]
                text += f"> {name} ({input['type']}){': ' + input['desc'] if input.get('desc') is not None else ''}\n"

        if len(self.outputs) > 0:
            text += "\nPipeline Outputs:\n"
            for component, name in self.outputs:
                output = self.components[component].outputs[name]
                text += f"< {name} ({output['type']}){': ' + output['desc'] if output.get('desc') is not None else ''}\n"

        metrics = [(name, metric, component_name) for component_name, component in self.components.items() if isinstance(component, PythonComponent) for name, metric in component.metrics.items()]
        if len(metrics) > 0:
            text += "\nMetrics:\n"
            for name, metric, _ in metrics:
                text += f"< {name}{': ' + metric['desc'] if metric.get('desc') is not None else ''}\n"

        if len(self.wiring) > 0:
            text += "\nI/O Wiring:\n"
            for component, name in self.inputs:
                text += f"  {name} -> {component}.{name}\n"
            for wire_hash in self.wiring:
                text += f"  {wire_hash}\n"
            for component, name in self.outputs:
                text += f"  {component}.{name} -> {name}\n"
            for name, metric, component_name in metrics:
                text += f"  {component_name}.{name} -> {name}\n"

        if self.periodicity is not None:
            text += "\nTimeshifting:\n"
            text += f"  Periodicity: {self.periodicity} ms\n"
            if len(self.timeshift_reference) > 0:
                text += "  References:\n"
                for ref in self.timeshift_reference:
                    text += f"  - {ref}\n"

        for component in self.components.values():
            text += "\n" + component.__repr__()

        return text

    def add_input(self, component, variable):
        """
        Defines an input variable on the given component as a pipeline input.

        Args:
            component (str): Name of the component
            variable (str): Name of the input variable
        """
        try:
            _ = self.components[component].inputs[variable]
        except KeyError:
            raise AssertionError("The component with input variable must exist in the pipeline.")

        if self.inputs is None:
            self.inputs = []

        if (component, variable) in self.inputs:
            raise AssertionError("The pipeline input already exists.")

        self.inputs.append((component, variable))

    def delete_input(self, component: str, variable: str):
        """
        Deletes a pipeline input.

        Args:
            component (str): Name of the component
            variable (str): Name of the input variable

        """
        if (component, variable) not in self.inputs:
            raise AssertionError("The pipeline input does not exist.")

        self.inputs.remove((component, variable))

    def add_output(self, component, variable):
        """
        Defines an output variable on the given component as a pipeline output.

        Args:
            component (str): Name of the component
            variable (str): Name of the output variable

        """
        try:
            _ = self.components[component].outputs[variable]
        except KeyError:
            raise AssertionError("The component with output variable must exist in the pipeline.")

        if self.outputs is None:
            self.outputs = []

        if (component, variable) in self.outputs:
            raise AssertionError("The pipeline output already exists.")

        self.outputs.append((component, variable))

    def delete_output(self, component: str, variable: str):
        """
        Deletes a pipeline output.

        Args:
            component (str): Name of the component
            variable (str): Name of the input variable

        """
        if (component, variable) not in self.outputs:
            raise AssertionError("The pipeline output does not exist.")

        self.outputs.remove((component, variable))

    def add_component(self, component: Component):
        """
        Adds a `Component` to the pipeline configuration without any connection.
        The `Component` can be marked as an input or output component of the pipeline.
        When these parameters are True, the `Component` is responsible for input or output data of the pipeline.
        The component must have a unique name. Two or more versions of the same component can not be added to the same pipeline with the same component name.

        Args:
            component (Component): `Component` to be added
        """

        if component.name in self.components:
            raise AssertionError(f"Component with name {component.name} already exists. Please rename the component.")
        self.components[component.name] = component

    def add_wiring(self, from_component: str, from_output: str, to_component: str, to_input: str):
        """
        Creates a one-to-one connection between the input and output of two components.
        The method checks if the connection is allowed with the following requirements:

        - The components exist with the given inputs/outputs
        - The given inputs and outputs are not connected to any wire
        - The types of the connected input and output are compatible

        Args:
            from_component (str): Name of the component which provides data to the `to_component`
            from_output (str): Name of the output variable of the `from_component`
            to_component (str): Name of the component which consumes data from the `from_component`
            to_input (str): Name of the input variable of the `to_component`
        """
        if from_component not in self.components:
            raise AssertionError(f"No component named '{from_component}'")
        if to_component not in self.components:
            raise AssertionError(f"No component named '{to_component}'")
        if from_output not in self.components[from_component].outputs:
            raise AssertionError(f"Component '{from_component}' has no output named '{from_output}'")
        if to_input not in self.components[to_component].inputs:
            raise AssertionError(f"Component '{to_component}' has no input named '{to_input}'")
        if self.get_wire_for_input(to_component, to_input) is not None:
            raise AssertionError(f"Input '{to_input}' of component '{to_component}' is already wired")

        _output_type = self.components[from_component].outputs[from_output]["type"]
        _input_type = self.components[to_component].inputs[to_input]["type"]
        if _output_type != _input_type:
            raise AssertionError("Output and input types do not match")

        wire_hash = self._wire_hash_string.format(from_component, from_output, to_component, to_input)
        self.wiring[wire_hash] = {
            "fromComponent": from_component,
            "fromOutput": from_output,
            "toComponent": to_component,
            "toInput": to_input,
        }

    def get_wire_for_output(self, component_name: str, output_name: str):
        """
        Searches for the wire which connects a component with `component_name` as data provider through its output with name output_name.

        Args:
            component_name (str): Name of the data provider component.
            output_name (str): Name of the output variable of `component_name`.

        Returns:
            [dict]: Wire which contains the data provider and receiver with their names and the names of their variables.
        """
        wires = [x for x in self.wiring.values() if x["fromComponent"] == component_name and x["fromOutput"] == output_name]
        return wires[0] if wires else None

    def get_wire_for_input(self, component_name: str, input_name: str):
        """
        Searches for the wire which connects a component with `component_name` as data consumer through its input with name `input_name`.

        Args:
            component_name (str): Name of the data consumer component.
            input_name (str): Name of the input variable of `component_name`.

        Returns:
            dict: Wire which contains the data provider and receiver with their names and the names of their variables.
        """
        wires = [x for x in self.wiring.values() if x["toComponent"] == component_name and x["toInput"] == input_name]
        return wires[0] if wires else None

    def delete_input_wire(self, component: str, variable: str, with_input: bool = True):
        """
        Deletes an existing connection between two components.
        The connection must be given with the name of the consumer component and its input variable.
        If an inter signal alignment reference variable is affected it cannot be deleted.
        By default, the input variable will be also deleted.

        Args:
            component (str): Name of the component which has the input given the name variable
            variable (str): Name of the input variable on the component which connected by the wire
            with_input (bool, optional): If set, the input variable will be also deleted from the component. Defaults to True.

        Raises:
            AssertionError: When the variable acts as inter signal alignment reference, it cannot be deleted, and an `AssertionError` will be raised.
        """
        wire = self.get_wire_for_input(component, variable)
        if wire is None:
            raise AssertionError(f"There is no wiring for input '{variable}' of component '{component}'")
        if variable in self.timeshift_reference:
            raise AssertionError("Inter signal alignment reference variables can not be deleted.")
        wire_hash = self._wire_hash_string.format(wire['fromComponent'], wire['fromOutput'], wire['toComponent'], wire['toInput'])
        self.wiring.pop(wire_hash)

        if with_input:
            self.components[component].delete_input(variable)

    def add_dependencies(self, packages: list):
        """
        @Deprecated, reason: components can have different Python versions and/or platform, therefore it's better to specify dependencies on a case-by-case basis.
        Collects the given Python packages with their versions from the executing Python environment and add them to all components of type `PythonComponent`.
        This step is necessary in order to execute the pipeline configuration on the Edge side.
        The method can be called multiple times but each time the previously-collected dependencies are cleared.
        The reason for this is to ensure a consistent dependency list for the `requirements.txt` file when the package is saved.

        Args:
            packages (list): List of the necessary python packages to execute the script defined by self.entrypoint
        """
        python_components = [self.components[name] for name in self.components if type(self.components[name]) is PythonComponent]
        for component in python_components:
            component.add_dependencies(packages)

    def set_timeshifting_periodicity(self, periodicity: int):
        """
        Enables inter-signal alignment with the given sampling period.

        With inter-signal alignment enabled, the AI Inference Server collects data for different input variables before it triggers the model.
        By default, `startingPoint` property is set to `First timestamp`, which means that inter-signal alignment is started at the
        first incoming value for any input variable.

        This property can be changed to `Signal reference` by adding inter-signal alignment reference variables
        via the `add_timeshifting_reference(..)` method. In this case, inter-signal alignment is started when the first value arrives
        for the defined input variables.

        Args:
            periodicity (int): Periodicity time in milliseconds for the AI Inference Server to perform inter-signal alignment. Valid range is [10, 2^31).
        """

        periodicity = int(periodicity)
        if periodicity not in range(10, int(math.pow(2, 31))):
            raise AssertionError("Inter signal alignment periodicity must be an integer and in range [10, 2^31)")

        self.periodicity = periodicity
        _logger.info(f"Inter signal alignment periodicity has been set to {self.periodicity}.")

    def add_timeshifting_reference(self, reference: str):
        """
        Enables signal alignment mode `Signal reference` by declaring input variables as reference variables.

        Args:
            reference (str): Variable name to be added to `self.timeshift_reference` list.
        """
        if reference not in [name for _, name in self.inputs]:
            raise AssertionError(f"There is no input variable defined with name '{reference}'")
        if reference in self.timeshift_reference:
            _logger.warning(f"Reference variable with name '{reference}' has been already added.")
            return
        self.timeshift_reference.append(reference)

    def remove_timeshifting_reference(self, reference: str):
        """
        Removes previously-defined inter-signal alignment reference variables.
        If no reference variables remain, the `startingPoint` will be `First timestamp`.

        Args:
            reference (str): Variable name to be removed from `self.timeshift_reference` list.
        """
        if reference not in self.timeshift_reference:
            raise AssertionError(f"Reference variable with name {'reference'} does not exist.")
        self.timeshift_reference.remove(reference)

    def get_pipeline_config(self):
        """
        Saves the information on the composed pipeline configuration package into a YAML file.

        This YAML file describes the components and the data flow between them for the AI Inference Server.
        The file is created in the `destination` folder with name `pipeline_config.yml`
        """
        if self.save_version is None:
            self.save_version = self.version
        if self.save_package_id is None:
            self.save_package_id = self.package_id

        pipeline_inputs = []
        pipeline_inputs += [{
            'name': name,
            'type': self.components[component_name].inputs[name]['type']
        } for component_name, name in self.inputs]

        pipeline_outputs = []
        pipeline_outputs += [{
            'name': name,
            'type': self.components[component_name].outputs[name]['type'],
            'metric': False,
        } for component_name, name in self.outputs]
        pipeline_outputs += [{
            'name': name,
            'type': 'String',
            'metric': True,
            'topic': f"/siemens/edge/aiinference/{self.name}/{self.save_version}/metrics/{component_name}/{name}",
        } for component_name, component in self.components.items() if isinstance(component, PythonComponent) for name in component.metrics.keys()]

        pipeline_dag = [{
            'source': f"{wire['fromComponent']}.{wire['fromOutput']}",
            'target': f"{wire['toComponent']}.{wire['toInput']}",
        } for wire in self.wiring.values()]
        pipeline_dag += [{
            'source': f'Databus.{name}',
            'target': f'{component_name}.{name}',
        } for component_name, name in self.inputs]
        pipeline_dag += [{
            'source': f'{component_name}.{name}',
            'target': f'Databus.{name}',
        } for component_name, name in self.outputs]
        pipeline_dag += [{
            'source': f'{component_name}.{name}',
            'target': f'Databus.{name}',
        } for component_name, component in self.components.items() if isinstance(component, PythonComponent) for name in component.metrics.keys()]

        config_yml_content = {
            'fileFormatVersion': '1.2.0',
            'dataFlowPipelineInfo': {
                'author': self.author,
                'createdOn': datetime.now(),
                'dataFlowPipelineVersion': self.save_version,
                'description': self.desc if self.desc else 'Created by AI SDK',
                'projectName': self.name,
                'packageId': str(self.save_package_id)
            },
            'dataFlowPipeline': {
                'components': [component._to_dict() for component in self.components.values()],
                'pipelineDag': pipeline_dag,
                'pipelineInputs': pipeline_inputs,
                'pipelineOutputs': pipeline_outputs,
            },
            'packageType': 'full'
        }
        if len(self.parameters.items()) != 0:
            config_yml_content["dataFlowPipeline"]["pipelineParameters"] = []
            for name, parameter in self.parameters.items():
                if parameter["topicBased"]:
                    config_yml_content["dataFlowPipeline"]["pipelineParameters"].append({
                        'name': name, 'type': parameter['type'],
                        'defaultValue': parameter['defaultValue'],
                        'topicBased': parameter['topicBased'], 'valueTopic': parameter['valueTopic']
                    })
                else:
                    config_yml_content["dataFlowPipeline"]["pipelineParameters"].append({
                        'name': name, 'type': parameter['type'],
                        'defaultValue': parameter['defaultValue']
                    })

        return config_yml_content

    def save_pipeline_config(self, destination):
        """
        Saves the information about the composed pipeline configuration package into a YAML file.

        This YAML file describes the components and the data flow between them for AI Inference Server.
        The file will be created in the `destination` folder with name `pipeline_config.yml`

        Args:
            destination (path-like): Path of the `destination` directory.
        """

        with open(Path(destination) / PIPELINE_CONFIG, "w") as f:
            yaml.dump(self.get_pipeline_config(), f)

    def get_datalink_metadata(self):
        """
        The method generates metadata information based on available information.

        Returns:
            dict: Dictionary with the necessary information for the AI Inference Server.
        """

        timeshifting = {
            "id": None,
            "enabled": False,
            "periodicity": self.periodicity,
            "startingPoint": None,
        }

        if self.periodicity is not None:
            timeshifting["enabled"] = True
            timeshifting["startingPoint"] = 'First timestamp'

        if len(self.timeshift_reference) > 0:
            timeshifting["startingPoint"] = 'Signal reference'

        exported_metadata = {
            "fileFormatVersion": "1.0.0",
            "id": None,
            "version": None,
            "createdOn": datetime.now(),
            "updatedOn": datetime.now(),
            "timeShifting": timeshifting,
            "inputs": [
                {
                    'name': _name,
                    'mapping': None,
                    'timeShiftingReference': _name in self.timeshift_reference,
                    'type': self.components[_component].inputs[_name]['type']
                } for _component, _name in self.inputs
            ]
        }
        return exported_metadata

    def save_datalink_metadata(self, destination):
        """
        Saves metadata for pipeline input variables.
        This method saves metadata for the AI Inference Server into a YAML file.
        This metadata determines how the AI Inference Server feeds input to the pipeline, especially inter-signal alignment.
        The file is created in the `destination` folder with the name `datalink_metadata.yml`

        Args:
            destination (path-like): Path of the destination directory.
        """
        with open(Path(destination) / DATALINK_METADATA, "w") as f:
            yaml.dump(self.get_datalink_metadata(), f)

    def save_telemetry_data(self, destination: Path):
        """
        Save telemetry data to a specified destination.

        Args:
            destination (Path): The path where the telemetry data should be saved.

        Returns:
            None

        Raises:
            None
        """
        telemetry_path = destination / TELEMETRY_YAML
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
        telemetry_data["industrial_ai"]["simaticai"] = MSG_NOT_FOUND
        telemetry_data["industrial_ai"]["vep-template-sdk"] = MSG_NOT_FOUND
        try:
            telemetry_data["industrial_ai"]["simaticai"] = pkg_resources.get_distribution("simaticai").version
        except pkg_resources.DistributionNotFound:
            _logger.debug("simaticai package not found")

        try:
            telemetry_data["industrial_ai"]["vep-template-sdk"] = pkg_resources.get_distribution("vep-template-sdk").version
        except pkg_resources.DistributionNotFound:
            _logger.debug("vep-template-sdk package not found")

        telemetry_data["pipeline"] = {}
        telemetry_data["pipeline"]["python_versions"] = list(set(self.components[component].python_version for component in self.components if isinstance(self.components[component], PythonComponent)))
        telemetry_data["pipeline"]["file_extensions"] = list(set(f.suffix for f in Path(destination).rglob("*") if f.suffix not in ["", ".zip", ".yml", ".yaml", ".html"]))

        yaml.dump(telemetry_data, open(telemetry_path, 'w'))

    def save_readme_html(self, destination):
        """
        Saves a `README.html` in the `destination` folder that describes the pipeline.

        Args:
            destination (path-like): Path of the destination folder.
        """
        pipelinePage = _PipelinePage(self)
        readme_html_path = Path(destination) / README_HTML
        readme_html_path.write_text(pipelinePage.__str__())

    def validate(self, destination="."):
        """
        Validates whether the package configuration is compatible with the expected runtime environment.

        The method verifies:

        - If the package has at least one component
        - If all wires create connections between existing components and their variables
        - If metadata is defined and valid.
        - If a package with the same name already exists in the `destination` folder. In this case a warning message appears and the `save(..)` method overwrites the existing package.
        - If the package has multiple components and if they are using the same Python version

        Args:
            destination (str, optional): Path of the expected destination folder. Defaults to ".".
        """
        if len(self.components) < 1:
            raise AssertionError("The package must have at least one component.")

        for name, variable in self.outputs:
            if self.components[name].batch.outputBatch:
                raise AssertionError(f"The component '{name}' has pipeline output defined with variable name '{variable}'. \
                                      None of component with pipeline output is allowed to provide batch output.")

        for wire_hash in self.wiring.copy():
            wire = self.wiring[wire_hash]
            self._check_wiring(wire, wire_hash)

        pipeline_inputs = [variable for _, variable in self.inputs]
        pipeline_outputs = [variable for _, variable in self.outputs]
        if any(variable in pipeline_outputs for variable in pipeline_inputs):
            conflicts = set(pipeline_inputs).intersection(set(pipeline_outputs))
            raise AssertionError(f"Pipeline input and output variables must be unique. Conflicting variables: {conflicts}")

        self._check_timeshifting()

        package_path = Path(destination) / f"{self.name}_{self.version}".replace(" ", "-")
        if package_path.is_dir():
            _logger.warning(f"Target folder ({package_path}) already exists! Unless changing the package name the package could be invalid and your files will be overwritten!")

        python_versions = set()

        for component in self.components:
            self.components[component].validate()

            if isinstance(self.components[component], PythonComponent):
                python_versions.add(self.components[component].python_version)

        if (1 < len(python_versions)):
            _logger.warning("The use of multiple python version in a single pipeline is not recommended. We recommend using only one of the supported versions, which are Python 3.10 or 3.11.")

        _logger.info(f"Package '{self.name}' is valid and ready to save.")

    def _check_timeshifting(self):
        if len(self.timeshift_reference) > 0 and self.periodicity is None:
            raise AssertionError("When using inter signal alignment reference variables, the periodicity must be set.")

    def _check_wiring(self, wire, wire_hash):
        error_messages = []
        if wire['fromComponent'] not in self.components:
            error_messages.append(f"From component {wire['fromComponent']} does not exist")
        if wire['toComponent'] not in self.components:
            error_messages.append(f"To component {wire['toComponent']} does not exist")
        if wire['fromOutput'] not in self.components[wire['fromComponent']].outputs:
            error_messages.append(f"Output variable {wire['fromOutput']} does not exist on component {wire['fromComponent']}")
        if wire['toInput'] not in self.components[wire['toComponent']].inputs:
            error_messages.append(f"Input variable {wire['toInput']} does not exist on component {wire['toComponent']}")
        if len(error_messages) == 0:
            from_type_ = self.components[wire['fromComponent']].outputs[wire['fromOutput']]['type']
            to_type_ = self.components[wire['toComponent']].inputs[wire['toInput']]['type']
            if from_type_ != to_type_:
                error_messages.append(f"The types of input and output variables does not match for wiring {wire_hash}.")
        if len(error_messages) > 0:
            self.wiring.pop(wire_hash)
            error_messages.append("The wire has been deleted, please check the variables and re-create the connection.")
            raise AssertionError(error_messages.__str__())

    def save(self, destination = ".", package_id: Optional[uuid.UUID] = None, version: Optional[str] = None) -> Path:
        """
        @Deprecated, reason: only edge package generation will be supported in the future. Use export instead.

        Saves the assembled package in a zip format.
        The name of the file is defined as `{package_name}_{package_version}.zip`.
        If a file with such a name already exists in the `destination` folder, it gets overwritten and a warning message appears.

        The package is also available as a subfolder on the destination path with the name `{package_name}_{package_version}`.
        If the assembled content does not meet the expected one, this content can be changed and simply packed into a zip file.

        The package contains files and folders in the following structure:

        - Package folder with name `{package_name}_{package_version}`
            - `datalink-metadata.yml`
            - `pipeline-config.yml`
            - Component folder with name `{component_name}`

            When the component is a `PythonComponent`, this folder contains:

            - `requirements.txt`
            - Entrypoint script defined by the entrypoint of the component
            - Extra files as added to the specified folders
            - Source folder with name `src` with necessary python scripts

        If a package ID is specified, and a package with the same ID and version is already present in the `destination` folder,
        an error is raised.

        Args:
            destination (str, optional): Target directory for saving the package. Defaults to ".".
            package_id (UUID): The optional package ID. If None, a new UUID is generated.
        """
        self.validate(destination)
        destination = Path(destination)
        if package_id is not None and not isinstance(package_id, uuid.UUID):
            package_id = uuid.UUID(package_id)

        prev_id = None
        prev_id_version = None
        prev_version, prev_with_id = self._find_previous(destination, package_id)
        if prev_with_id is not None:
            prev_id_version, prev_id = prev_with_id

        if package_id == prev_id and (version or self.version) == str(prev_id_version):
            raise RuntimeError(f"package with version '{version or self.version}' and id '{package_id}' already exists")

        self.save_version = version if version is not None \
            else self.version if self.version is not None \
            else "1" if package_id is not None and prev_id is not None and package_id != prev_id \
            else str(prev_id_version + 1) if prev_id_version is not None \
            else str(prev_version + 1) if prev_version is not None and prev_id is None \
            else "1"

        self.save_package_id = package_id if package_id is not None \
            else prev_id if prev_id is not None \
            else uuid.uuid4()

        name = self.name.replace(" ", "-")
        package_name = f"{name}_{self.save_version}"
        package_file = destination / f"{package_name}.zip"
        specified_version_is_decimal = version is not None and version.isdecimal() or self.version is not None and self.version.isdecimal()
        if specified_version_is_decimal:
            if package_file.exists():
                p_id = self._extract_package_id(package_file, False)
                if p_id is not None and p_id == package_id:
                    raise RuntimeError(f"package with version '{self.save_version}' and id '{self.save_package_id}' already exists: '{package_file}'")
            edge_package_file = destination / f"{name}-edge_{self.save_version}.zip"
            if edge_package_file.exists():
                p_id = self._extract_package_id(edge_package_file, True)
                if p_id is not None and p_id == package_id:
                    raise RuntimeError(f"package with version '{self.save_version}' and id '{self.save_package_id}' already exists: '{edge_package_file}'")

        destination = destination / package_name
        destination.mkdir(parents=True, exist_ok=True)

        # Save
        for component in self.components:
            self.components[component].save(destination, False)
            if isinstance(self.components[component], PythonComponent):
                self.report_writer.add_direct_dependencies(self.components[component].name, self.components[component].python_dependencies.dependencies)

        self.save_datalink_metadata(destination)
        self.save_pipeline_config(destination)
        self.save_readme_html(destination)
        self.save_telemetry_data(destination)

        zip_destination = shutil.make_archive(
            base_name=str(destination.parent / package_name), format='zip',
            root_dir=destination.parent, base_dir=package_name,
            verbose=True, logger=_logger)

        pipeline_size = os.path.getsize(zip_destination)  # zipped package size in bytes
        pipeline_size_GB = "{:.2f}".format(pipeline_size / 1000 / 1000 / 1000)
        pipeline_size_limit_GB = "{:.2f}".format(PIPELINE_SIZE_LIMIT / 1000 / 1000 / 1000)
        if pipeline_size > PIPELINE_SIZE_LIMIT:
            error_msg = f"Pipeline size {pipeline_size} bytes ({pipeline_size_GB} GB) exceeds the limit of " \
                        f"{PIPELINE_SIZE_LIMIT} bytes ({pipeline_size_limit_GB} GB). " \
                        "Please remove unnecessary files and dependencies and try again."

            _logger.error(error_msg)
            raise RuntimeError(error_msg)

        return Path(zip_destination)

    # TODO: refactor the business logic in PBI 1662648
    def _find_previous(self, destination: Path, package_id: Optional[uuid.UUID] = None) -> Tuple[Optional[int], Optional[Tuple[int, uuid.UUID]]]:
        latest_version = None
        latest_with_id = None

        if Path(destination).is_dir() is False:
            return None, None
                
        for file in destination.glob(f"{self.name.replace(' ', '-')}*.zip"):

            zip_version, zip_package_id = self._extract_package_info(file)
            
            if not zip_version.isdecimal():
                continue
            zip_version = int(zip_version)

            if zip_package_id is None:  # package id in the zip package not present
                if latest_version is None or zip_version > latest_version:
                    latest_version = zip_version
            elif package_id is None:
                if latest_with_id is None or zip_version > latest_with_id[0]:
                    latest_with_id = (zip_version, zip_package_id)
            else:
                if package_id != zip_package_id:
                    continue
                if latest_with_id is None or zip_version > latest_with_id[0]:
                    latest_with_id = (zip_version, zip_package_id)

        return latest_version, latest_with_id

    def _extract_package_info(self, zip_path: Path) -> Tuple:
        with zipfile.ZipFile(zip_path) as zip_file:
            config_path = next(f for f in zip_file.namelist() if f.endswith("pipeline_config.yml"))
            with zip_file.open(config_path) as config_file:
                config = yaml.load(config_file, Loader=yaml.SafeLoader)
                pipeline_info = config.get("dataFlowPipelineInfo", {})
                version = pipeline_info.get("dataFlowPipelineVersion", None)
                package_id = pipeline_info.get("packageId", None)
                package_id = uuid.UUID(package_id) if package_id is not None else None
                return version, package_id

    def _extract_package_id(self, package_file: Path, is_edge_package: bool) -> Optional[uuid.UUID]:
        try:
            with OpenZipInTemp(package_file) as package_dir:
                if not is_edge_package:
                    package_dir = package_dir / package_file.stem
                with open(package_dir / 'pipeline_config.yml') as config_file:
                    return uuid.UUID(yaml.load(config_file, Loader=yaml.SafeLoader)["dataFlowPipelineInfo"]["packageId"])
        except Exception:
            _logger.debug(f"Could not extract Package ID from '{package_file}'")
            return None

    def export(self, destination = ".", package_id: Optional[uuid.UUID] = None, version: Optional[str] = None) -> Path:
        """
        Export a runnable pipeline package.

        Args:
            destination (str): optional target directory for saving the package. Defaults to ".".
            package_id (UUID): optional package ID. If None, a new UUID is generated.
            version (str): optional version. If None, an automatic version number is generated.
        """
        config_package = None
        try:
            config_package = self.save(destination, package_id, version)
            runtime_package = convert_package(config_package, self.report_writer)
            return runtime_package
        finally:
            if config_package is not None:
                Path(config_package).unlink(missing_ok=True)

    def add_parameter(self, name, default_value, type_name: str = "String", topic_based: bool = False, desc: str = None):
        """
        Adds a parameter to the pipeline configuration, which alters the behavior of the pipeline.
        The parameter's default value and its properties are saved in the pipeline configuration
        and the value of the parameter can later be changed on AI Inference Server.

        Args:
            name (str): Name of the parameter
            desc (str): Description of the parameter (optional)
            type_name (str, optional): Data type of the parameter. Defaults to "String".
            default_value (str): Default value of the parameter
            topic_based (bool, optional): If true, the parameter can be updated from a message queue.

        Raises:

            ValueError:
                When:
                - the default value of the parameter is not of the specified data type (`type_name`) or
                - the specified data type itself is not an allowed data type (not a part of `parameter_types` dict) or
                - the specified data type is not given in the right format or
                - the type of the given `topic_based` parameter is not `bool`.
        """
        parameter_types = {
            "String": 'str',
            "Integer": 'int',
            "Double": 'float',
            "Boolean": 'bool'
        }

        default_value_type = type(default_value).__name__

        if type_name not in parameter_types.keys():
            raise ValueError(f"The given value type is not supported. Please use one of these: {parameter_types.keys()}")

        if default_value_type != parameter_types[type_name]:
            raise ValueError(f"The given value type does not match the type of '{type_name}'. Please use the correct one from these: {list(parameter_types.keys())}")

        if not isinstance(topic_based, bool):
            raise ValueError("Type of the given `topic_based` parameter is not `bool`.")

        self.parameters[name] = {
            "name": name,
            "type": type_name,
            "defaultValue": default_value,
            "topicBased": topic_based,
            "valueTopic": None
        }
        if desc is not None:
            self.parameters[name]["desc"] = desc

def convert_package(zip_path: str or os.PathLike, report_writer: Optional[PipelineReportWriter] = None) -> Path:
    """
    @Deprecated, reason: only edge package generation will be supported in the future. Use Pipeline.export(...) instead.

    Create an Edge Configuration Package from a given Pipeline Configuration Package.

    If the input zip file is `{path}/{name}_{version}.zip`, the output file will be created as `{path}/{name}-edge_{version}.zip`.
    Please make sure that the given zip file comes from a trusted source!

    If a file with such a name already exists, it is overwritten.

    First, this method verifies that the requirements identified by name and version are either included
    in `PythonPackages.zip` or available on pypi.org for the target platform.

    Currently, the supported edge devices run Linux on 64-bit x86 architecture, so the accepted Python libraries are restricted to the platform independent ones and packages built for 'x86_64' platforms.
    AI Inference Server also provides a Python 3.10 and runtime environment, so the supported Python libraries are restricted to Python 3.10 and 3.11 compatible packages.

    If for the target platform the required dependency is not available on pypi.org
    and not present in `PythonPackages.zip`,  it will log the problem at ERROR level.
    Then it downloads all dependencies (either direct or transitive), and creates a new zip
    file, which is validated against the AI Inference Server's schema.
    This functionality requires pip with version of 21.3.1 or greater.

    This method can be used from the command line too.
    Example usage:
    ```
    python -m simaticai convert_package <path_to_pipeline_configuration_package.zip>
    ```

    Args:
        zip_path (path-like): path to the pipeline configuration package zip file.
        report_writer (ReportWriter, optional): a ReportWriter object to write the report for a pipeline. Defaults to None.

    Returns:
        os.PathLike: The path of the created zip file.

    Exceptions:
        PipelineValidationError: If the validation fails. See the logger output for details.
    """
    zip_path = Path(zip_path)
    if zip_path.stem.find('_') < 0:
        raise AssertionError("The input zip file name must contain an underscore character.")
    with tempfiles.OpenZipInTemp(zip_path) as zip_dir:
        top_level_items = list(zip_dir.iterdir())
        if len(top_level_items) != 1:
            raise AssertionError("The Pipeline Configuration Package must contain a single top level directory.")
        package_dir = zip_dir / top_level_items[0]
        runtime_dir = zip_dir / "edge_config_package"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        config = yaml_helper.read_yaml(package_dir / PIPELINE_CONFIG)
        _validate_with_schema("input pipeline_config.yml", config, "pipeline.schema.json")
        runtime_config = _generate_runtime_config(config)
        if report_writer is not None:
            # TODO: consider moving zip_path to the parameter of report_writer.write_report()
            report_writer.set_path(Path(zip_path.parent / f"{zip_path.stem}_package_report.md"))
            report_writer.set_pipeline_config(config)
        
        for component in config['dataFlowPipeline']['components']:
            source_dir = package_dir / component["name"]

            if component["runtime"]["type"] == "python":
                python_version = component['runtime']['version']
                try:
                    python_version_validator(python_version)
                except ValueError as error:
                    raise AssertionError(error)

                dependency_set = _package_component_dependencies(source_dir, python_version)
                if report_writer is not None:
                    report_writer.add_full_dependency_set(component_name=component["name"], dependency_set=dependency_set)
                runtime_config["runtimeConfiguration"]["components"].append({
                    "name": component["name"],
                    "device": "IED1",
                    "targetRuntime": "Python",
                })

            if component["runtime"]["type"] == "gpuruntime":
                runtime_config["runtimeConfiguration"]["components"].append({
                    "name": component["name"],
                    "device": "IED1",
                    "targetRuntime": "gpuruntime",
                })

            _package_component(source_dir, runtime_dir / 'components' / f"{component['name']}_{component['version']}")

        if report_writer is not None:
            report_writer.write_report()
        _logger.info(f"Report on {zip_path.stem} is saved to {zip_path.parent}.")
        shutil.copy(str(package_dir / PIPELINE_CONFIG), str(runtime_dir / PIPELINE_CONFIG))
        datalink_metadata_yaml = package_dir / DATALINK_METADATA
        if datalink_metadata_yaml.is_file():
            shutil.copy(str(datalink_metadata_yaml), runtime_dir / DATALINK_METADATA)

        _validate_with_schema(f"generated {RUNTIME_CONFIG}", runtime_config, "runtime.schema.json")
        with open(runtime_dir / RUNTIME_CONFIG, "w", encoding="utf8") as file:
            yaml.dump(runtime_config, file)

        readme_html = package_dir / README_HTML
        if readme_html.exists():
            (runtime_dir / README_HTML).write_text(readme_html.read_text())

        telemetry_yaml = package_dir / TELEMETRY_YAML
        if telemetry_yaml.exists():
            (runtime_dir / TELEMETRY_YAML).write_text(telemetry_yaml.read_text())

        edge_package_path = Path(shutil.make_archive(
            # One Pythonic Way to replace the last occurrence of "_" with "-edge".
            base_name=str(PurePath(zip_path).parent / "-edge_".join(zip_path.stem.rsplit("_", 1))),
            format='zip',
            root_dir=runtime_dir,
            verbose=True,
            logger=_logger))

        sha256_hash = calc_sha(edge_package_path)
        sha_format = f"{sha256_hash}  {edge_package_path.name}"
        edge_package_path.with_suffix('.sha256').write_text(sha_format)

        return edge_package_path


def _package_component(source_dir, target_name):
    return shutil.make_archive(
        base_name=target_name,
        format='zip',
        root_dir=source_dir,
        verbose=True,
        logger=_logger)


def _package_component_dependencies(component_dir: Path, python_version: str) -> set:
    python_packages_folder = component_dir / 'packages'
    requirements_file_path = component_dir / REQUIREMENTS_TXT
    packages_file = component_dir / PYTHON_PACKAGES_ZIP
    dependency_set = set()

    python_packages_folder.mkdir(exist_ok=True)

    if packages_file.is_file():
        with zipfile.ZipFile(packages_file) as zip_file:
            zip_file.extractall(python_packages_folder)
        packages_file.unlink()
    requirements_file_path.touch(exist_ok=True)
    try:
        dependency_set = create_wheelhouse(requirements_file_path, python_version, python_packages_folder)

        if any(Path(python_packages_folder).iterdir()):
            shutil.make_archive(
                base_name=str(component_dir / PYTHON_PACKAGES),
                format='zip',
                root_dir=python_packages_folder,
                verbose=True,
                logger=_logger)
    finally:
        shutil.rmtree(python_packages_folder)

    # This filtering needs to happen here, not in PythonDependencies,
    # because create_wheelhouse still needs the original requirements.txt
    # with the extra index urls.
    with open(requirements_file_path, "r") as f:
        lines = f.readlines()
    filtered_lines = list(filter(lambda x: not (x.startswith("# Extra") or x.startswith("--extra-index-url") or x.startswith("# Index") or x.startswith("--index-url")), lines))
    with open(requirements_file_path, "w") as f:
        f.writelines(filtered_lines)

    return dependency_set


def _generate_runtime_config(pipeline_config: dict):
    project_name = pipeline_config["dataFlowPipelineInfo"]["projectName"]

    return {
        "fileFormatVersion": "1",
        "runtimeInfo": {
            "projectName": project_name,
            "runtimeConfigurationVersion": "1.0.0",
            "createdOn": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "runtimeConfiguration": {
            "devices": [{
                "name": "IED1",
                "address": "localhost",  # Optional
                "arch": "x86_64",  # Optional, TODO: validate target keys
            }],
            "components": [],
        },
    }


def _validate_with_schema(name: str, data: dict, schema: str):
    try:
        jsonschema.validate(
            instance=data,
            schema=json.load(module_resources.open_text("simaticai.data.schemas", schema))
            # TODO: after upgrading to python 3.9
            # schema=json.load(resources.files("simaticai") / "data" / "schemas" / "pipeline.schema.json")
        )
    except jsonschema.exceptions.ValidationError as e:
        raise AssertionError(f"""Schema validation failed for {name} using '{schema}'!
    message: {e.message}
    $id: {e.schema['$id']}
    title: {e.schema['title']}
    description: {e.schema['description']}
    """) from None


def _get_pipeline_info(pipeline_config: str):
    pipeline_config = yaml_helper.read_yaml(pipeline_config)
    pipeline_info = pipeline_config["dataFlowPipelineInfo"]
    pipeline_info["packageType"] = pipeline_config.get("packageType", "full")
    pipeline_info["originVersion"] = pipeline_config.get("originVersion", None)
    return pipeline_info


def _validate_delta_package_inputs(origin_package_info: dict, new_package_info: dict):
    if origin_package_info["packageType"] == "delta" or new_package_info["packageType"] == "delta":
        raise AssertionError("Neither of the packages can be delta package!")

    if origin_package_info["projectName"] != new_package_info["projectName"]:
        raise AssertionError("The new edge package must have the same name as the origin edge package!")

    if origin_package_info["dataFlowPipelineVersion"] == new_package_info["dataFlowPipelineVersion"]:
        raise AssertionError("The new edge package can not have the same version as the origin edge package!")


def _change_pipeline_config(config_path: str, origin_package_version: str):
    data = yaml_helper.read_yaml(config_path)
    data["packageType"] = "delta"
    data["originVersion"] = origin_package_version
    with open(config_path, "w") as f:
        yaml.dump(data, f)


def _extract_edge_package(edge_package_zip_path: str, path_to_extract: Path):
    zipfile.ZipFile(edge_package_zip_path).extractall(path_to_extract)
    for f in path_to_extract.rglob("*.zip"):
        component_path = path_to_extract / "components" / f.stem
        packages = Path(component_path, PYTHON_PACKAGES_ZIP)

        zipfile.ZipFile(f).extractall(component_path)
        if packages.is_file():
            zipfile.ZipFile(component_path / PYTHON_PACKAGES_ZIP).extractall(component_path / PYTHON_PACKAGES)
            os.remove(packages)
        os.remove(f)
    return path_to_extract


def _copy_file(file_path: Path, from_dir: Path, to_dir: Path):
    new_path = to_dir / file_path.relative_to(from_dir)
    new_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(file_path, to_dir / file_path.relative_to(from_dir))


def create_delta_package(origin_edge_package_zip_path: str, new_edge_package_zip_path: str):
    """
    Creates a Delta Edge Configuration Package from two given Edge Configuration Packages.
    The created Delta Configuration Package is applicable to import into AI Inference Server,
    if the Original Edge Configuration Package is already imported there.
    The Delta Configuration Package only contains the additions and modifications
    in the New Edge Configuration Package compared to the Original one.
    That also means that no file deletion is possible in a deployed pipeline via this option.
    Please make sure that both of the given zip files come from a trusted source!

    Usage:
    ~~~python
    delta_package_path = deployment.create_delta_package('Edge-Config-edge-1.0.0.zip', 'Edge-Config-edge-1.1.0.zip')
    ~~~

    This method can be used from the command line, too.
    ```
    python -m simaticai create_delta_package <origin_package.zip> <modified_package.zip>
    ```

    Once the package is calculated, you will have an `Edge-Config-edge-delta-1.1.0.zip` file beside the updated package zip file.
    <ul>This package will contain
    <li><ul>the three configuration file for the package;
        <li>pipeline_config.yml</li>
        <li>runtime_config.yml</li>
        <li>datalink_metadata.yml</li>
    </li></ul>
    <li>the newly added files,</li>
    <li>and the updated files.</li>
    </ul>

    The package will not contain any information on the deleted files and they will be copied from the original pipeline.

    **Caution!**
    *If you change the version of a component in the pipeline, the delta package will contain all the files of the component because AI Inference Server identifies
    a component with a different version as a different component!*

    Args:
        origin_edge_package_zip_path (str): Path to the origin edge configuration package zip file.
        new_edge_package_zip_path (str): Path to the new edge configuration package zip file.

    Returns:
        os.PathLike: The path of the created delta edge package zip file.

    Raises:

        AssertionError:
            When:
            - either of the given edge packages is a delta package or
            - the names of the given edge packages differ or
            - the versions of the given edge packages are equal.
    """

    workdir = Path(tempfile.mkdtemp(prefix="aisdk_deltapack-"))
    delta_dir  = Path(workdir / "delta")
    delta_dir.mkdir(parents=True)

    origin_dir = _extract_edge_package(origin_edge_package_zip_path, Path(workdir / "orig"))
    new_dir    = _extract_edge_package(new_edge_package_zip_path, Path(workdir / "new"))

    origin_package_info = _get_pipeline_info(origin_dir / PIPELINE_CONFIG)
    new_package_info = _get_pipeline_info(new_dir / PIPELINE_CONFIG)

    _validate_delta_package_inputs(origin_package_info, new_package_info)

    files_in_new_package = new_dir.rglob("*")
    for f in files_in_new_package:
        if f.is_dir():
            continue
        orig_file_path = origin_dir / f.relative_to(new_dir)
        if not orig_file_path.exists():
            _copy_file(f, new_dir, delta_dir)
        else:
            checksum_original = calc_sha(orig_file_path)
            checksum_new = calc_sha(f)
            if checksum_original != checksum_new:
                _copy_file(f, new_dir, delta_dir)

    _change_pipeline_config(delta_dir / PIPELINE_CONFIG, origin_package_info["dataFlowPipelineVersion"])

    new_edge_package_zip_path = Path(new_edge_package_zip_path)
    delta_path = _zip_delta_package(delta_dir, new_edge_package_zip_path)

    shutil.rmtree(workdir, ignore_errors=True)
    return Path(delta_path)


def _zip_delta_package(delta_dir: Path, new_package_path: Path):
    target_folder = new_package_path.parent
    splitted_name = str(new_package_path.stem).split("_")
    target_name = "_".join(splitted_name[:-1]) + "_delta_" + "".join(splitted_name[-1:])

    for dir in Path(delta_dir / "components").glob("*"):
        if Path(dir / PYTHON_PACKAGES).is_dir():
            shutil.make_archive(dir / PYTHON_PACKAGES, "zip", dir / PYTHON_PACKAGES)
            shutil.rmtree(dir / PYTHON_PACKAGES)
        shutil.make_archive(dir, "zip", dir)
        shutil.rmtree(dir)

    delta_path = shutil.make_archive(target_folder / target_name, "zip", delta_dir)
    return delta_path


class _PipelinePage(markup.page):

    def __init__(self, pipeline: Pipeline):
        super().__init__('strict_html', 'lower')

        self.twotags.append("section")
        self.init(
            title=f"{pipeline.name} ({pipeline.version})",
            doctype="<!DOCTYPE html>",
            charset="utf-8",
            lang="en")

        self.section()

        self.h1(f"Pipeline {pipeline.name} ({pipeline.version})")
        if pipeline.desc:
            self.p(pipeline.desc)
        self.html_generate_parameters(pipeline)
        self.html_generate_pipeline_inputs(pipeline)
        self.html_generate_pipeline_outputs(pipeline)
        self.html_generate_io_wiring(pipeline)
        self.html_generate_timeshifting(pipeline)

        for component in pipeline.components.values():
            self.html_generate_components(component)

        self.section.close()

    def html_generate_components(self, component: Component):
        self.hr()
        self.section()

        self.h1(f"{component.__class__.__name__} {component.name}")
        if component.desc:
            self.p(component.desc)
        self.html_generate_component_inputs(component)
        self.html_generate_component_outputs(component)
        self.html_generate_metrics(component)
        if issubclass(component.__class__, PythonComponent):
            self.html_generate_resources(component)
            self.html_generate_entrypoints(component)

        self.section.close()

    def html_generate_parameters(self, pipeline: Pipeline):
        if len(pipeline.parameters) > 0:
            self.strong("Parameters")
            self.ul()

            for name, parameter in pipeline.parameters.items():
                self.li()
                self.i(f"{name} ({parameter['type']}, default: '{parameter['defaultValue']}')")
                self.br()
                if parameter.get('desc') is not None:
                    self.span(parameter['desc'])
                self.li.close()

            self.ul.close()

    def html_generate_pipeline_inputs(self, pipeline: Pipeline):
        if len(pipeline.inputs) > 0:
            self.strong("Inputs")
            self.ul()

            for component, name in pipeline.inputs:
                input = pipeline.components[component].inputs[name]
                self.li()
                self.i(f"{name} ({input['type']})")
                self.br()
                if input.get('desc') is not None:
                    self.span(input['desc'])
                self.li.close()
            self.ul.close()

    def html_generate_pipeline_outputs(self, pipeline: Pipeline):
        if len(pipeline.outputs) > 0:
            self.strong("Outputs")
            self.ul()

            for component, name in pipeline.outputs:
                output = pipeline.components[component].outputs[name]
                self.li()
                self.i(f"{name} ({output['type']})")
                self.br()
                if output.get('desc') is not None:
                    self.span(output['desc'])
                self.li.close()

            self.ul.close()

    def html_generate_component_inputs(self, component: Component):
        self.strong("Inputs")
        self.ul()

        for name, input in component.inputs.items():
            self.li()
            self.i(f"{name} ({input['type']})")
            self.br()
            if input.get('desc') is not None:
                self.span(input['desc'])
            self.li.close()

        self.ul.close()

    def html_generate_component_outputs(self, component: Component):
        self.strong("Outputs")
        self.ul()

        for name, output in component.outputs.items():
            self.li()
            self.i(f"{name} ({output['type']})")
            self.br()
            if output.get('desc') is not None:
                self.span(output['desc'])
            self.li.close()

        self.ul.close()

    def html_generate_io_wiring(self, pipeline: Pipeline):
        if len(pipeline.wiring) > 0:
            self.strong("I/O Wiring")
            self.ul()

            for component, name in pipeline.inputs:
                self.li(f"{name} &#8594 {component}.{name}")
            for wire_hash in pipeline.wiring:
                self.li(wire_hash.replace("->", "&#8594"))
            for component, name in pipeline.outputs:
                self.li(f"{component}.{name} &#8594 {name}")

            self.ul.close()

    def html_generate_timeshifting(self, pipeline: Pipeline):
        if pipeline.periodicity is not None:
            self.strong("Timeshifting")
            self.ul()
            self.li(f"Periodicity: {pipeline.periodicity} ms")
            self.ul.close()

            if len(pipeline.timeshift_reference) > 0:
                self.strong("References")
                self.ul()
                for ref in pipeline.timeshift_reference:
                    self.li(ref)
                self.ul.close()

    def html_generate_resources(self, component: Component):
        if isinstance(component, PythonComponent) and component.resources is not None and len(component.resources) > 0:
            self.strong("Resources")
            self.ul()
            for path, base in component.resources.items():
                self.li(f"{base}/{path.name}".replace('./', ''))
            self.ul.close()

    def html_generate_entrypoints(self, component: Component):
        if isinstance(component, PythonComponent) and component.entrypoint is not None:
            self.strong("Entrypoint")
            self.ul()
            self.li(component.entrypoint.name)
            self.ul.close()

    def html_generate_metrics(self, component: Component):
        if isinstance(component, PythonComponent) and component.metrics is not None and len(component.metrics) > 0:
            self.strong("Metrics")
            self.ul()
            for name, metric in component.metrics.items():
                self.li()
                self.i(name)
                if metric.get('desc') is not None:
                    self.br()
                    self.span(metric['desc'])
                self.li.close()
            self.ul.close()


class GPURuntimeComponent(Component):
    """
    The GPURuntimeComponent is used to define a component that runs on a GPU device.
    The component works only with ONNX models and can be used in an Inference Pipeline.

    Attributes:
        name (str): Component name.
        version (str): Component version.
        desc (str): Component description.

    Methods:
        use_model(self,
                    path: Union[Path, str], max_batch_size: int,
                    optimization: Optional[model_config.TensorRTOptimization] = None,
                    warmup: model_config.Warmup = None)
            Add an ONNX model file for the component.

        use_config(self, path: Union[Path, str])
            Use a custom config.pbtxt file instead of the autogenerated one.

        save(self, destination: Union[Path, str], validate = False)
            Saves the component to a folder structure, so it can be used as part of a pipeline configuration package.
    """

    def __init__(self, name: str = "inference", version: str = "1", desc: str = ""):
        """
        Creates a new, empty GPU Runtime component.

        Args:
            name (str): Component name. (default: inference)
            version (str): Component version. (default: 1)
            desc (str): Component description (optional)
        """
        super().__init__(name=name, desc=desc)
        self.version = version
        self.entrypoint: Union[Path, None] = None
        self.model_path: Union[Path, None] = None
        self.model_version: str = "1"
        self.config: Union[Path, None] = None
        self.auto_config = None

    def _to_dict(self):
        return {
            **super()._to_dict(),
            'version': self.version,
            'entrypoint': f"{self.model_version}/{self.entrypoint.name}",
            'hwType': 'GPU',
            'runtime': {
                'type': 'gpuruntime',
                'version': '0.1.0',
            }
        }

    def use_model(self, path: Union[Path, str],
                  max_batch_size: int,
                  optimization: Optional[model_config.TensorRTOptimization] = None,
                  warmup: model_config.Warmup = None):
        """
        Add the ONNX model file for the component.

        Args:
            path (Union[Path, str]): The path to the ONNX model file.
            max_batch_size (int): The maximum batch size for the model.
            optimization (model_config.TensorRTOptimization, optional): The optimization configuration for the model. Defaults to None.
            warmup (model_config.Warmup, optional): The warmup configuration for the model. Defaults to None.

        Raises:
            AssertionError: If the specified model file is not found, has an invalid extension, or if max_batch_size is less than 0.

        """
        path = Path(path)

        if not path.is_file():
            raise AssertionError(f"specified model file not found: '{path}'")

        if path.suffix != ".onnx":
            raise AssertionError(f"model file extension is not '.onnx': '{path}'")

        if max_batch_size < 0:
            raise AssertionError("max_batch_size must be greater or equal to 0")

        self.entrypoint = Path("model.onnx")
        self.model_path = path
        if self.config is not None:
            _logger.warning("Previously added configuration was removed. Component will use the default configuration unless you specify your own.")
        self.config = None

        # Remove old automatic variables
        if self.auto_config is not None:
            for var in self.auto_config.inputs:
                self.delete_input(var["name"])
            for var in self.auto_config.outputs:
                self.delete_output(var["name"])

        self.auto_config = model_config.ModelConfig(onnx_path=path,
                                                    max_batch_size=max_batch_size,
                                                    warmup=warmup,
                                                    optimization=optimization)
        for var in self.auto_config.inputs:
            self.add_input(var["name"], var["type"])
        for var in self.auto_config.outputs:
            self.add_output(var["name"], var["type"])

    def use_config(self, path: Union[Path, str]):
        """
        Sets the configuration file to be used for inference.
        Intended usage is to use a custom configuration file instead of the autogenerated one.
        This way extra configurations can be added to the component, such as the execution accelerator.

        Args:
            path (Union[Path, str]): The path to the configuration file.

        Raises:
            AssertionError: If the specified config file is not found or has an invalid extension.

        """
        path = Path(path)

        if not path.is_file():
            raise AssertionError(f"specified config file not found: '{path}'")

        if path.suffix != ".pbtxt":
            raise AssertionError(f"config file extension is not '.pbtxt': '{path}'")

        _validate_gpuruntime_config(path)

        self.config = path

    def save(self, destination: Union[Path, str], validate = False):
        """
        Saves the component to a folder structure, so it can be used as part of a pipeline configuration package.

        The component folder contains the following:

        - An `.onnx` model file
        - A `.pbtxt` configuration file

        Args:
            destination (path-like): Target directory to which the component will be saved.
        """
        if self.entrypoint is None:
            raise AssertionError("An ONNX model file must be specified before the component can be saved.")

        component_dir = Path(destination) / self.name
        component_dir.mkdir(parents = True, exist_ok = True)

        model_dir = component_dir / self.model_version
        model_dir.mkdir(exist_ok = True)

        shutil.copy(self.model_path, model_dir / "model.onnx")

        if self.config is None:
            _logger.warning("Configuration was not specified. Model will be saved with default configuration.")
            (component_dir / "config.pbtxt").write_text(f"{self.auto_config}")
        else:
            shutil.copy(self.config, component_dir)

def _validate_gpuruntime_config(path: Union[Path, str]):
    with open(path, 'r') as file:
        text_format.Parse(file.read(), model_config_pb2.ModelConfig())

