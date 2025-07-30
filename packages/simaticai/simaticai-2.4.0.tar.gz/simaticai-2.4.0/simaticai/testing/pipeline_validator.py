# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

"""
Static validation of pipeline packages.

Executes static checks on a pipeline configuration package including:

- Verifying that the Python version required in the package is supported by a known version of the AI Inference Server.
- Verifying that all the required Python packages are either included in the pipeline package itself or available on `pypi.org` for the target platform.
"""
import subprocess
from pathlib import Path
import zipfile
import logging

from simaticai import deployment
from simaticai.helpers import tempfiles, yaml_helper
from simaticai.packaging.constants import REQUIREMENTS_TXT, PYTHON_PACKAGES_ZIP
from simaticai.packaging.wheelhouse import create_wheelhouse

logging.basicConfig()
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

INVALID_PIPELINE_PACKAGE_MESSAGE = "Invalid pipeline configuration package. Perhaps you have passed an Edge configuration package instead?"

class PipelineValidationError(Exception):
    """
    Represents a problem with the pipeline configuration.

    Args:
        description (str): Description of the error. Mandatory argument.
    """
    def __init__(self, description: str) -> None:
        assert description is not None
        self.value = description

    def __str__(self):
        return self.value


def validate_pipeline_dependencies(zip_path):
    """
    @Deprecated, reason: In the future only the edge package will be generated and the same validation is performed during edge package creation.

    Validates an already built pipeline configuration package to check if it is compatible with the AI Inference Server.

    This method verifies that the requirements identified by name and version are either included
    in `PythonPackages.zip` or available on pypi.org for the target platform.
    If the required dependency for the target platform is not available on pypi.org
    and not present in `PythonPackages.zip` it will log the problem at the ERROR level.

    Args:
        zip_path (path-like): Path to the pipeline configuration package zip file

    Raises:
        `pipeline_validator.PipelineValidationError` if the validation fails. See the logger output for details.
    """
    with tempfiles.OpenZipInTemp(zip_path) as package_dir:
        package_dir = next(package_dir.iterdir())
        error = read_config_and_download_deps(package_dir)
        if error:
            raise PipelineValidationError("Requirements of one or more components can not be satisfied.")
    _logger.info(f"Validating pipeline package '{zip_path}' was successful.")


def download_component_dependencies(component: dict, package_dir: Path):
    """
    Download the dependencies of a pipeline component.

    Args:
        component (dict): A single component from the parsed `pipeline_configuration.yml`.
        package_dir (Path): The directory where the component was extracted
    """
    _logger.info(f"Validating requirements of component: {component['name']}")
    try:
        deployment.python_version_validator(component['runtime']['version'])
    except ValueError as error:
        raise PipelineValidationError(error)

    component_dir = package_dir / component['name']
    requirements_file_path = component_dir / REQUIREMENTS_TXT

    python_packages_folder = _build_python_packages_folder(component_dir)

    return not _are_dependencies_available(requirements_file_path, component['runtime']['version'], python_packages_folder)


def read_config_and_download_deps(package_dir: Path):
    """
    Reads the pipeline configuration from the package directory and downloads its dependencies

    Args:
        package_dir (Path): The directory where the pipeline configuration package was extracted.

    Returns:
        boolean: True if there was an error during the download of the components, False otherwise
    """
    try:
        config = yaml_helper.read_yaml(package_dir / 'pipeline_config.yml')
        error = False
        for component in config['dataFlowPipeline']['components']:
            error = download_component_dependencies(component, package_dir) or error
        return error
    except Exception:
        raise PipelineValidationError(INVALID_PIPELINE_PACKAGE_MESSAGE)


def _are_dependencies_available(requirements_file_path: Path, python_version: str, python_packages_folder: Path):
    try:
        if Path(requirements_file_path).is_file():
            try:
                create_wheelhouse(requirements_file_path, python_version, python_packages_folder)
            except RuntimeError as error:
                _logger.error(f"Error occurred while creating wheelhouse\n{error.__str__()}")
                return False
            except AssertionError as error:
                _logger.error(f"Could not find a package that satisfies the requirements\n{error.__str__()}")
                return False
            return True
        else:
            _logger.info(f"'{REQUIREMENTS_TXT}' was not found.")
    except subprocess.TimeoutExpired:
        _logger.error("TimeoutExpired occurred during download")
        return False
    except Exception as e:
        _logger.error(f"Unexpected exception occurred while downloading packages\n{e.__str__()}")
        return False
    return True


def _build_python_packages_folder(component_dir: Path) -> Path:
    assert component_dir is not None

    python_packages_folder = component_dir / 'packages'
    packages_file = component_dir / PYTHON_PACKAGES_ZIP

    python_packages_folder.mkdir(exist_ok=True)

    if packages_file.is_file():
        with zipfile.ZipFile(packages_file) as zip_file:
            zip_file.extractall(python_packages_folder)

    return python_packages_folder
