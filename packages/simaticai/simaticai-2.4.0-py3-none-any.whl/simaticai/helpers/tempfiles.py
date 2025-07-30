# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

"""
Module for dealing with temporary files.

This module helps with extracting a zip file into a temporary folder.
"""

import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Union


class OpenZipInTemp:
    """
    Unzip a zip archive into a temporary directory.

    Example usage:

        with OpenZipInTemp("path_to_zip_file.zip") as temp_dir:
            # do something with temp_dir
            pass

    Args:
        zip_path (path-like): path to the archive.
    """

    def __init__(self, zip_path: Union[str, os.PathLike], clean_up: bool = True):
        if not zipfile.is_zipfile(zip_path):
            raise ValueError(f"File does not exist or not a zip file: {zip_path}")

        self.zip_path = zip_path
        self.tmp_path = None
        self.clean_up = clean_up

    def __enter__(self) -> Path:
        self.tmp_path = Path(tempfile.mkdtemp(prefix="unzip-"))
        with zipfile.ZipFile(self.zip_path, "r") as zip_file:
            zip_file.extractall(path=self.tmp_path)
        return self.tmp_path

    def __exit__(self, e_type, e_val, e_trace):
        if self.clean_up:
            shutil.rmtree(self.tmp_path, ignore_errors=True)
