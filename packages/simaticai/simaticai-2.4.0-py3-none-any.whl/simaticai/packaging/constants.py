# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

"""
Common constants used in 'packaging' module.
"""

README_HTML = "README.html"
REQUIREMENTS_TXT = "requirements.txt"
PYTHON_PACKAGES = "PythonPackages"
PYTHON_PACKAGES_ZIP = f"{PYTHON_PACKAGES}.zip"
PIPELINE_CONFIG = "pipeline_config.yml"
DATALINK_METADATA = "datalink_metadata.yml"
RUNTIME_CONFIG = "runtime_config.yml"
TELEMETRY_YAML = "telemetry_data.yml"

MSG_NOT_FOUND = "not found"

PIPELINE_SIZE_LIMIT = int(2.2 * 1000 * 1000 * 1000)  # zipped pipeline size limit of 2.2 GB


# Based on https://code.siemens.com/siemens-ai-launcher-sail/ai-on-edge/sail-pipes-orchestrator/sail-pipes-orchestrator-ui/-/blob/developer/src/app/models/databus/connector.constant.ts?ref_type=heads#L199

supported_types = [
    'Boolean',
    'Integer',
    'Double',
    'String',
    'BooleanArray',
    'IntegerArray',
    "UInt8Array",
    "UInt16Array",
    "UInt32Array",
    "UInt64Array",
    "Int8Array",
    "Int16Array",
    "Int32Array",
    "Int64Array",
    'DoubleArray',
    "Float16Array",
    "Float32Array",
    "Float64Array",
    'StringArray',
    'Object',
    'Binary',
    'ImageSet',
]
"""
List of input/output data types supported by AI Inference Server.

Custom types can also be provided when specifying pipeline inputs/outputs, but AI SDK will raise a warning message in this case.
"""


PLATFORMS = [
    "any",
    "manylinux1_x86_64",
    "manylinux2010_x86_64",
    "manylinux2014_x86_64",
    "linux_x86_64"
] + [ f"manylinux_2_{glibc_minor}_x86_64" for glibc_minor in range(5,32) ]
""" List of platform tags supported by AI Inference Server. """
