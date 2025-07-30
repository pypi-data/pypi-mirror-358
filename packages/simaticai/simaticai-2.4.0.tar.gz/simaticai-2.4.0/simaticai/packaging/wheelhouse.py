# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

"""
Methods for downloading and validating dependencies

This module collects all the necessary methods for downloading
wheel or source distributions, and validation methods for checking if
the whole collection could be installed in the AI Inference Server's
Python runtime environment.
"""

import os
import subprocess
import sys
import shutil
import zipfile
import tarfile
import tempfile
import json
import logging
from pathlib import Path
from itertools import chain
from typing import Union
from textwrap import dedent
from email.parser import Parser

from simaticai.helpers import pep508
from .constants import PLATFORMS, REQUIREMENTS_TXT

logging.basicConfig()
logging.getLogger().handlers = [logging.StreamHandler(sys.stdout)]
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

_ERROR_LINE = "ERROR: No matching distribution found for "
report_json_path = lambda tmp_dir: Path(tmp_dir) / "report.json"

LIMITED_PACKAGES = {
    "tensorflow": "WARNING: TensorFlow is imported. For better performance with an already "
                  "trained model, consider using TensorFlow Lite (tflite) instead.",
    "opencv_python": "WARNING: opencv-python is currently not supported by AI Inference Server, "
                     "please use opencv-python-headless instead.",
}

def assert_none_parameters(**kwargs):
    """
    Checks if any of the given parameters are None.
    Returns: 
        True if all parameters are not None, 
    Raises:
        AssertionError: otherwise.
    """

    none_values = [k for k, v in kwargs.items() if v is None]
    if 0 < len(none_values):
        none_values = ", ".join(none_values)
        raise AssertionError(f"Parameters can not be None: {none_values}")
    return True

def is_wheel_file(path: os.PathLike) -> bool:
    """
    Checks whether the file on the given `path` is a wheel file.

    Args:
        path (path-like): The relative or absolute path of the wheel file.
    Returns:
        bool: True if the zipfile contains a WHEEL text file, False otherwise.
    """
    if zipfile.is_zipfile(path):
        _wheel = zipfile.ZipFile(path)
        return 'WHEEL' in [f.split("/")[-1] for f in _wheel.namelist()]

    return False


def is_source_file(path: os.PathLike) -> bool:
    """
    Checks whether the file on the given `path` is a python source distribtion file.

    Args:
        path (path-like): The relative or absolute path of the zip or tar.gz archive file.
    Returns:
        bool: True if the archive file contains a PKG-INFO text file, False otherwise.
    """

    if zipfile.is_zipfile(path):
        _archive = zipfile.ZipFile(path)
        return 'PKG-INFO' in [f.split("/")[-1] for f in _archive.namelist()]

    if tarfile.is_tarfile(path):
        with tarfile.open(path) as _archive:
            return 'PKG-INFO' in [f.split("/")[-1] for f in _archive.getnames()]

    return False


def _extract_pkg_info(archive_path: Union[str, os.PathLike]):
    if tarfile.is_tarfile(archive_path):
        archive = tarfile.open(archive_path, "r")
        files = archive.getnames()
        get_text = lambda filename: archive.extractfile(filename).read().decode("utf-8")
    elif zipfile.is_zipfile(archive_path):
        archive = zipfile.ZipFile(archive_path, "r")
        files = archive.namelist()
        get_text = lambda filename: archive.read(filename).decode("utf-8")
    else:
        return None
    PKG_INFO = list(filter(lambda filepath: filepath.endswith('PKG-INFO'), files))
    headers = None
    if 0 < len(PKG_INFO):
        headers = map(get_text, PKG_INFO)
        headers = map(lambda txt: Parser().parsestr(text=txt, headersonly=True), headers)
        headers = list(headers)
    archive.close()
    return headers


def is_pure_python_source(archive_path: Union[str, os.PathLike]):
    """
    Checks whether the given source distribution contains only Python sources.

    This method handles source distributions in a unified way.
    It searches for 'PKG-INFO' files, collects the programming languages
    used in the source, and returns True if only the Python language was used.

    Args:
        archive_path (path-like): The relative or absolute path of the zip or tar.gz archive file.
    Returns:
        bool: True if the archive file contains only Python sources.
    """
    headers = _extract_pkg_info(archive_path)
    if headers is None:
        return False
    classifiers = map(lambda header: header.get_all("classifier"), headers)
    classifiers = map(lambda classifier: [] if classifier is None else classifier, classifiers)
    classifiers = chain.from_iterable(classifiers)
    programming_languages = filter(lambda line: line.startswith('Programming Language ::'), classifiers)
    programming_languages = map(lambda line: line.split("::")[1].strip().lower(), programming_languages)
    return all(map(lambda txt: txt == 'python', programming_languages))


def get_wheel_name_version(archive_path: Union[str, os.PathLike]):
    """
    Extracts the package name and version from a wheel file.

    Args:
        archive_path (path-like): The relative or absolute path of the wheel archive file.
    Returns:
        (str, str): The name and version of the wheel if successful, (None,None) otherwise.
    """
    with zipfile.ZipFile(archive_path, "r") as archive:
        files = archive.namelist()
        METADATA = list(filter(lambda filepath: filepath.endswith('METADATA'), files))
        if 0 < len(METADATA):
            headers = map(
                lambda filename: archive.read(filename).decode("utf-8"),
                METADATA)
            headers = map(lambda txt: Parser().parsestr(text=txt, headersonly=True), headers)
            headers = list(headers)[0]
            name = headers.get("name")
            version = headers.get("version")
            return (name, version)
    return (None, None)


def get_sdist_name_version(archive_path: Union[str, os.PathLike]):
    """
    Extracts the package name and version from a source distribution file.

    Args:
        archive_path (path-like): The relative or absolute path of the zip or tar.gz archive file.
    Returns:
        (str, str): The name and version of the source distribution if successful, (None,None) otherwise.
    """
    headers = _extract_pkg_info(archive_path)
    if headers is None:
        return (None, None)
    headers = headers[0]
    name = headers.get("name")
    version = headers.get("version")
    return (name, version)


def _pip_download_platform_wheels(requirements_file_path: Path, python_version: str, python_packages_folder: Path, extra_index=[]):
    assert_none_parameters(
        requirements_file_path  = requirements_file_path, 
        python_version          = python_version, 
        python_packages_folder  = python_packages_folder
    )
    command_line = [
        sys.executable, "-m", "pip", "download",
        "--no-color",
        "-r", f"{requirements_file_path.resolve()}",
        "-d", f"{python_packages_folder.resolve()}",
        "--find-links", f"{python_packages_folder.resolve()}",
        "--python-version", f"{python_version}",
        "--only-binary=:all:", "--no-binary=:none:"
    ]
    for platform in PLATFORMS:
        command_line += ["--platform", platform]
    for i in extra_index:
        parts = i.split(" ")
        command_line += parts
    return subprocess.run(command_line, stderr=subprocess.PIPE, text=True)


def _pip_download_source_dist(requirements_file_path: Path, python_packages_folder: Path, extra_index):
    
    assert_none_parameters(
        requirements_file_path  = requirements_file_path,
        python_packages_folder  = python_packages_folder
    )

    command_line = [
        sys.executable, "-m", "pip", "download",
        "--no-color",
        "-r", f"{requirements_file_path.resolve()}", "setuptools",
        "-d", f"{python_packages_folder.resolve()}",
        "--find-links", f"{python_packages_folder.resolve()}",
        "--no-deps",
    ]
    for i in extra_index:
        parts = i.split(" ")
        command_line += parts
    return subprocess.run(command_line, stderr=subprocess.PIPE, text=True)


def _pip_get_source_dependencies(requirements_file_path: Path, python_packages_folder: Path, report_path: Path, extra_index):
    assert_none_parameters(
        requirements_file_path  = requirements_file_path,
        python_packages_folder  = python_packages_folder,
        report_path             = report_path
    )
    
    command_line = [
        sys.executable, "-m", "pip", "install",
        "-r", f"{requirements_file_path.resolve()}",
        "--no-color",
        "--target", f"{python_packages_folder.resolve()}",
        "--find-links", f"{python_packages_folder.resolve()}",
        "--dry-run", "--ignore-installed", "--force-reinstall",
        "--report", f"{report_path.resolve()}",
    ]
    for i in extra_index:
        parts = i.split(" ")
        command_line += parts
    return subprocess.run(command_line, stderr=subprocess.PIPE, text=True)


def _pip_dry_install_packages(python_version: str, python_packages_folder: Path, report_path: Path):
    assert_none_parameters(
        python_version          = python_version,
        python_packages_folder  = python_packages_folder,        
    )
    
    command_line = [
        sys.executable, "-m", "pip", "install",
        "--no-color",
        "--dry-run", "--ignore-installed", "--force-reinstall", "--no-index",
        "--target", f"{python_packages_folder.resolve()}",
        "--find-links", f"{python_packages_folder.resolve()}",
        "--python-version", f"{python_version}",
        "--only-binary=:all:", "--no-binary=:none:",
        "--report", f"{report_path.resolve()}",
    ]
    for platform in PLATFORMS:
        command_line += ["--platform", platform]
    command_line += [ str(f.resolve()) for f in Path(python_packages_folder).iterdir() ]
    return subprocess.run(command_line, stderr=subprocess.PIPE, text=True)


def check_directory_has_only_wheels_and_pure_sdist(python_packages_folder: Union[str, os.PathLike]):
    """
    Checks all files in a directory if they are wheel files or pure Python source distributions.

    Args:
        python_packages_folder (path-like): The relative or absolute path of the directory to be checked.
    Raises:
        AssertionError: If the directory contains other files than wheels or pure Python source distributions.
    """
    not_pure = []
    for file in list(python_packages_folder.iterdir()):
        if not (is_wheel_file(file) or is_pure_python_source(file)):
            not_pure.append(file.name)
    if 0 < len(not_pure):
        not_pure = "\n".join(not_pure)
        raise AssertionError(dedent(f"""
            One or more source dependencies are not pure Python sources.
            You need to convert them to wheel files for the target platform manually.
            List of not pure Python source distributions:
            {not_pure}
            """))

def remove_setuptools(python_packages_folder):
    filename = [f for f in Path(python_packages_folder).glob("setuptools*")]
    if len(filename):
        filename[0].unlink()

def consistency_check(requirements_file_path: Union[str, os.PathLike], python_version: str,
                      python_packages_folder: Union[str, os.PathLike], report_path: Union[str, os.PathLike], check_pure: bool = True):
    result = _pip_dry_install_packages(python_version, python_packages_folder, report_path)
    _check_report_for_dependency_limitations(report_path)
    remove_setuptools(python_packages_folder)
    if 0 != result.returncode:
        raise AssertionError(f"Dependency checking failed for file '{requirements_file_path}'.\n{result.stderr}")
    if check_pure:
        check_directory_has_only_wheels_and_pure_sdist(python_packages_folder)


def _extract_transitive_dependency_info(requirements, sources, src_path, python_packages_folder, tmp, extra_index):
    new_requirements = {}
    report_json = report_json_path(tmp)
    report_json.unlink(missing_ok=True)
    result = _pip_get_source_dependencies(src_path, python_packages_folder, report_json, extra_index)
    if 0 == result.returncode:
        report = json.loads(report_json.read_text())
        for dep in report['install']:
            name = dep['metadata']['name']
            vers = dep['metadata']['version']
            if (name not in sources.keys()) and (name not in requirements.keys()):
                new_requirements[name] = pep508.parse_line(f"{name}=={vers}")
    return new_requirements


def _separate_wheels_and_sdists(requirements: dict, sources: dict, python_version: str, python_packages_folder: Union[str, os.PathLike], req_path, src_path, extra_index):
    has_src_dep = 0 < len(requirements.values())
    counter = 100
    while has_src_dep:
        if (0 == counter):
            raise AssertionError("It looks like the specified requirements have caused an infinite download loop. Terminating.")
        counter -= 1
        with open(req_path, "w") as f:
            for spec in requirements.values():
                f.write(str(spec) + "\n")
        with open(src_path, "w") as f:
            for spec in sources.values():
                f.write(str(spec) + "\n")
        # Try to download requirements for the target platform, and see what fails
        result = _pip_download_platform_wheels(req_path, python_version, python_packages_folder, extra_index)
        if 0 == result.returncode:
            has_src_dep = False
        else:
            for line in result.stderr.split("\n"):
                if _ERROR_LINE in line:
                    spec_line = line.split(_ERROR_LINE)[1]
                    spec_line = spec_line.split("\x1b")[0].strip()
                    spec: pep508.Spec = pep508.parse_line(spec_line)
                    sources[spec.name] = requirements.pop(spec.name)
            has_src_dep = 0 < len(requirements.values())
    with open(req_path, "w") as f:
        for spec in requirements.values():
            f.write(str(spec) + "\n")
    with open(src_path, "w") as f:
        for spec in sources.values():
            f.write(str(spec) + "\n")
    return (requirements, sources)


def _compose_dependencies(requirements_file_path: Union[str, os.PathLike], python_version: str, python_packages_folder: Union[str, os.PathLike], check_pure: bool = True):
    """
    Given a requirements.txt with some source distributions specified,
    this method
        - separates wheel and source dependencies
        - downloads platform specific wheels
        - downloads the source distributions without their dependencies
        - runs a dry install on the requirements collected so far
        - processes the report.json for further dependencies
        - repeats the whole process until all source and platform specific wheels are downloaded
        - runs a dry install on the package directory to check if it would install
        - checks if all the source distributions are pure python sources
        - raises an error if there are sources in other language
    """
    tmp = Path(tempfile.mkdtemp())
    req_path = tmp / REQUIREMENTS_TXT
    src_path = tmp / "sources.txt"
    report_path = report_json_path(tmp)
    req_path.touch(exist_ok=True)
    src_path.touch(exist_ok=True)
    report_path.touch(exist_ok=True)
    try:
        requirements, extra_index, index_url = pep508.parse_requirements(requirements_file_path)
        if index_url is not None:
            extra_index.append(index_url)
        sources = {}
        has_src_transitive_dep = True
        while has_src_transitive_dep:
            requirements, sources = _separate_wheels_and_sdists(requirements, sources, python_version, python_packages_folder, req_path, src_path, extra_index)
            if 0 == len(sources.values()):
                has_src_transitive_dep = False
            else:
                result = _pip_download_source_dist(src_path, python_packages_folder, extra_index)
                if 0 != result.returncode:
                    raise AssertionError(f"Requirements file '{requirements_file_path}' contains invalid dependency specifications:\n{result.stderr}")
                new_requirements = _extract_transitive_dependency_info(requirements, sources, src_path, python_packages_folder, tmp, extra_index)
                if 0 == len(new_requirements.keys()):
                    has_src_transitive_dep = False
                else:
                    for name, spec in new_requirements.items():
                        requirements[name] = spec
        consistency_check(requirements_file_path, python_version, python_packages_folder, report_path, check_pure)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _download_only_wheels_if_possible(requirements_file_path: Union[str, os.PathLike], python_version: str, python_packages_folder: Union[str, os.PathLike]):
    """
    @Deprecated, reason: This method can be removed in SDK 2.0, since the `separate_wheels_and_sdists` method does the same thing, if there are no sdist dependencies. Kept only for preserving backward compatibility.
    """
    result = _pip_download_platform_wheels(requirements_file_path, python_version, python_packages_folder)
    src_dep = False
    for line in result.stderr.split("\n"):
        if _ERROR_LINE in line:
            src_dep = True
            break
    if (0 != result.returncode) and not src_dep:
        _logger.warning(f"Downloading wheels failed, reason:\n{result.stderr}")
        raise RuntimeError(f"Downloading wheels failed, reason:\n{result.stderr}")
    return 0 == result.returncode


def _check_package_for_dependency_limitations(package_name: str):
    if package_name is None:
        return
    limited_package_message = LIMITED_PACKAGES.get(package_name.replace('-','_').lower())
    if limited_package_message:
        _logger.warning(limited_package_message)


def _check_report_for_dependency_limitations(report_path: Union[str, os.PathLike]):
    """
    Checks the report.json file for dependency limitations.
    """
    report = json.loads(report_path.read_text(encoding='utf-8') or "{}")
    for dep in report.get('install', []):
        name = dep['metadata']['name']
        _check_package_for_dependency_limitations(name)


def create_wheelhouse(requirements_file_path: Union[str, os.PathLike], python_version: str, python_packages_folder: Union[str, os.PathLike]):
    dependency_set = set()
    # try the easy way
    success = _download_only_wheels_if_possible(requirements_file_path, python_version, python_packages_folder)
    if success:
        if not any(python_packages_folder.iterdir()):
            return dependency_set
        try:
            tmp = Path(tempfile.mkdtemp())
            report_path = report_json_path(tmp)
            result = _pip_dry_install_packages(python_version, python_packages_folder, report_path)
            if 0 != result.returncode:
                raise RuntimeError(f"Dry install failed, reason:\n{result.stderr}")
            _check_report_for_dependency_limitations(report_path)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    else:
        # let's do this the hard way
        try:
            _compose_dependencies(requirements_file_path, python_version, python_packages_folder)
        except AssertionError as error:
            raise RuntimeError(f"Downloading wheels and source distributions failed, reason:\n{str(error)}")

    for package in python_packages_folder.iterdir():
        if is_source_file(package):
            dependency_set.add(get_sdist_name_version(package))
        elif is_wheel_file(package):
            dependency_set.add(get_wheel_name_version(package))
        else:
            # TODO what to do when there is a different kind of file in the packages folder?
            pass
    return dependency_set
