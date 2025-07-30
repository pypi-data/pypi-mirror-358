# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

"""
Helpers.

This module contains functionality that does not belong to the main domain of the `simaticai` module.


"""

import hashlib
import os
from pathlib import Path
from typing import Union


def calc_sha(file_path: Union[str, os.PathLike]):
    file_path = Path(file_path)
    data_buffer = memoryview(bytearray(262144))
    sha_generator  = hashlib.sha256()
    with open(file_path, 'rb', buffering=0) as file:
        for n in iter(lambda: file.readinto(data_buffer), 0):
            sha_generator.update(data_buffer[:n])
    return sha_generator.hexdigest()
