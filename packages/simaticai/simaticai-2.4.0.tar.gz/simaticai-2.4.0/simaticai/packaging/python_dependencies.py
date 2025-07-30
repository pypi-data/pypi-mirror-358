# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

"""
Python dependencies

This class handles specifying and validating Python dependencies.
"""

import os
import sys
import logging
import shutil
import tempfile
import zipfile
import requests
import urllib
from pathlib import Path
from typing import Union

from simaticai.helpers import pep508
from .constants import REQUIREMENTS_TXT, PYTHON_PACKAGES
from .wheelhouse import is_wheel_file, is_pure_python_source, get_wheel_name_version, get_sdist_name_version, _check_package_for_dependency_limitations

logging.basicConfig()
logging.getLogger().handlers = [logging.StreamHandler(sys.stdout)]
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

_GPU_DEPENDENCIES = [
    'torch',
    'torchaudio',
    'torchvision',
    'ultralytics',
    'ultralyticsheadless'
]

_PYTORCH_CPU_REPO_URL = 'https://download.pytorch.org/whl/cpu'
_PYPI_REPO_URL = 'https://pypi.org/simple'

REPO_MODIFICATION_WARNING_MSG = "Pytorch GPU dependencies were replaced with CPU only Pytorch version. " \
    f"Using {_PYTORCH_CPU_REPO_URL} as the primary repository."
ADDED_PYPI_WARNING_MSG = f"Extra index url list was prepended with {_PYPI_REPO_URL}."
INDEX_URL_MOVED_WARNING_MSG = "User defined index url was moved to extra index url list."


class PythonDependencies():

    def __init__(self, python_version='3.11', dir: Union[str, os.PathLike] = None):
        """
        This class handles Python dependencies

        Dependencies from remote repositories can be added via a requirements.txt file,
        or by calling the add_dependencies method. Dependencies can also be added as
        a single wheel or source distribution file, or as a collection in a zip archive
        via the add_python_packages method.

        The class can be converted to string, which will contain the dependencies
        in PEP508 format.
        """
        self.python_version = python_version
        self.dependencies = {}
        self.python_packages = Path(tempfile.mkdtemp(dir=dir, prefix="dependencies_"))
        self.temp = Path(tempfile.mkdtemp(dir=dir, prefix="temp_"))

        self.optimize_dependencies = True
        self.index_url = None
        self.extra_index = []

    def __str__(self):
        """
        PEP508 representation of the dependencies.
        """
        result = ""
        if self.index_url is not None:
            result += '# Index URL\n'
            result += f"{self.index_url}\n"
        if len(self.extra_index) > 0:
            result += "# Extra index urls\n"
            for url in self.extra_index:
                result += f"{url}\n"
        result += "# Runtime dependencies\n"
        for spec in self.dependencies.values():
            result += str(spec) + "\n"
        return result

    def __repr__(self):
        return self.__str__()

    def clear(self):
        self.dependencies.clear()
        self.extra_index = []
        self.index_url = None
        shutil.rmtree(self.python_packages, ignore_errors=True)
        shutil.rmtree(self.temp, ignore_errors=True)
        self.python_packages.mkdir(mode=0o700, exist_ok=True)
        self.temp.mkdir(mode=0o700, exist_ok=True)
        _logger.warning("Previously added dependencies have been removed.")

    def set_requirements(self, requirements_path: Union[str, os.PathLike]):
        self.clear()

        dependencies, extra_index, index_url = pep508.parse_requirements(requirements_path)

        for name, spec in dependencies.items():
            _check_package_for_dependency_limitations(spec.name)
            if not any(spec.name.lower() == dep.lower() for dep in self.dependencies):
                self.dependencies[name] = spec
                _logger.info(f"Runtime dependency added: {spec}")
            else:
                _logger.warning(f"Dependency already exists: {spec}")
        if index_url is not None:
            self.index_url = index_url
            _logger.info(f"Index url added: {index_url}")
        for url in extra_index:
            self.extra_index.append(url)
            _logger.info(f"Extra index url added: {url}")

    def add_dependencies(self, packages: list):
        for package in packages:
            if isinstance(package, tuple):
                name, version = package
                spec = pep508.parse_line(f"{name}=={version}")
            else:
                spec = pep508.parse_line(f"{package}")

            _check_package_for_dependency_limitations(spec.name)

            if not any(spec.name.lower() == dep.lower() for dep in self.dependencies):
                self.dependencies[spec.name] = spec
                _logger.info(f"Runtime dependency added: {spec}")
            else:
                _logger.warning(f"Dependency already exists: {spec}")

    def add_python_packages(self, path: Union[str, os.PathLike]) -> None:
        path: Path = Path(path)
        if not path.is_file():
            raise AssertionError(f"The file must be available on path {path.resolve()}")
        specs = []
        tmp = None
        if is_wheel_file(path):
            name, version = get_wheel_name_version(path)
            specs.append((name, version, path))
        elif is_pure_python_source(path):
            name, version = get_sdist_name_version(path)
            specs.append((name, version, path))
        elif zipfile.is_zipfile(path):
            tmp = Path(tempfile.mkdtemp(dir=self.temp))
            zip = zipfile.ZipFile(path)
            for pkg in zip.namelist():
                zip.extract(pkg, path=tmp)
                file = tmp / Path(pkg).name
                if is_wheel_file(file):
                    name, version = get_wheel_name_version(file)
                    specs.append((name, version, file))
                elif is_pure_python_source(file):
                    name, version = get_sdist_name_version(file)
                    specs.append((name, version, file))
                else:
                    _logger.warning(f"File skipped because it is not a wheel or pure python source: {pkg}")
        else:
            _logger.warning(f"File skipped because it is not a wheel or pure python source or a zip file: {path}")
        for name, version, path in specs:
            if name is not None:
                if version is None:
                    spec = pep508.parse_line(f"{name}")
                else:
                    spec = pep508.parse_line(f"{name}=={version}")

                _check_package_for_dependency_limitations(spec.name)

                if not any(spec.name.lower() == dep.lower() for dep in self.dependencies):
                    shutil.copy(path, self.python_packages)
                    self.dependencies[spec.name] = spec
                    _logger.info(f"Runtime dependency added: {spec}")
                else:
                    _logger.warning(f"Dependency already exists: {spec}")
        if tmp is not None:
            shutil.rmtree(tmp, ignore_errors=True)

    def _download_or_copy_dependency(self, name, version):
        dependency_url = urllib.parse.urlparse(version)  # raises ValueError if the url is invalid
        dependency_path = Path(urllib.parse.unquote(dependency_url.path))
        filename = dependency_path.name

        if "file" == dependency_url.scheme:
            # Possible Exceptions here: FileNotFoundError, PermissionError, OSError, IsADirectoryError, SameFileError
            if not dependency_path.is_file():
                raise FileNotFoundError(f"The dependency '{name}' can not be found on path '{dependency_path}'")

            if (self.python_packages / filename).is_file():
                _logger.warning(f"Dependency '{name}' will not be copied because it already exists in '{self.python_packages}' folder.")
            else:
                _logger.info(f"Dependency '{name}' will be copied to '{self.python_packages}' folder.")
                shutil.copy(dependency_path.resolve(), self.python_packages)
        else:
            # Possible Exceptions here: requests.exceptions.RequestException
            _logger.info(f"Dependency '{name}@{version}' will be downloaded from the repository.")

            response = requests.get(version)
            response.raise_for_status()

            with open(self.python_packages / filename, "wb") as f:
                f.write(response.content)
        return self.python_packages / filename

    def save(self, folder_path):
        # Downloads dependencies specified with url from remote repositories or copies them from local file system
        # Does not work with source distributed packages
        for name, dependency in self.dependencies.copy().items():
            if isinstance(dependency.version, str):
                try:
                    path = self._download_or_copy_dependency(name, dependency.version)
                    _, version = get_wheel_name_version(path)
                    self.dependencies[name] = pep508.parse_line(f"{name}=={version}")

                except requests.exceptions.RequestException as request_error:
                    raise RuntimeError(f"Failed to download dependency '{dependency.name}=={dependency.version}' from the repository.") from request_error

        requirements_file_path = folder_path / REQUIREMENTS_TXT
        with open(requirements_file_path, "w") as f:
            f.write(str(self))

        shutil.make_archive(
            base_name = folder_path / PYTHON_PACKAGES,
            root_dir = self.python_packages,
            format = 'zip',
            verbose = True,
            logger = _logger)

    def _check_if_index_url_is_set_to_pytorch_cpu(self):
        if self.index_url is None:
            return False
        if self.index_url.strip().startswith("--index-url") and _PYTORCH_CPU_REPO_URL in self.index_url:
            return True
        return False

    def enable_dependency_optimization(self):
        self.optimize_dependencies = True

    def disable_dependency_optimization(self):
        self.optimize_dependencies = False

    def validate(self):
        for spec in self.dependencies.values():
            _check_package_for_dependency_limitations(spec.name)

        found_gpu_dependency = any(dep in _GPU_DEPENDENCIES for dep in self.dependencies)
        if not found_gpu_dependency:
            return

        if self.optimize_dependencies:
            if self.index_url is None:
                self.index_url = f"--index-url {_PYTORCH_CPU_REPO_URL}"
                added_pypi_warning = ""
                if not any([_PYPI_REPO_URL in item for item in self.extra_index]):
                    self.extra_index.insert(0, f"--extra-index-url {_PYPI_REPO_URL}")
                    added_pypi_warning = ADDED_PYPI_WARNING_MSG
                _logger.warning(f"WARNING! {REPO_MODIFICATION_WARNING_MSG} {added_pypi_warning}")

            elif self._check_if_index_url_is_set_to_pytorch_cpu():
                if not any([_PYPI_REPO_URL in item for item in self.extra_index]):
                    self.extra_index.insert(0, f"--extra-index-url {_PYPI_REPO_URL}")
                    _logger.warning(f"WARNING! {REPO_MODIFICATION_WARNING_MSG} {ADDED_PYPI_WARNING_MSG}")

            else:
                user_defined_index_url = self.index_url.replace("--index-url", "--extra-index-url", 1)
                self.index_url = f"--index-url {_PYTORCH_CPU_REPO_URL}"
                self.extra_index.insert(0, user_defined_index_url)
                _logger.warning(f"WARNING! {REPO_MODIFICATION_WARNING_MSG} {INDEX_URL_MOVED_WARNING_MSG}")

        else:
            if not self._check_if_index_url_is_set_to_pytorch_cpu():
                _logger.warning(
                    "WARNING! The resulting package could contain unused GPU dependencies "
                    "which considerably increase the file size.")
