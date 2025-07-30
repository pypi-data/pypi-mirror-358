# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

import os
from onnx import load, TensorProto
import logging
from typing import Optional, Union
from enum import Enum


_logger = logging.getLogger(__name__)

# TODO: clarify which elem_type in onnx is supported and find appropriat aiis type
tensor_type_dict = {
    TensorProto.FLOAT: { "data_type": "TYPE_FP32", "aiis_type": "Float32Array"},
    TensorProto.UINT8: { "data_type": "TYPE_UINT8", "aiis_type": "Uint8Array"},
    TensorProto.INT8: { "data_type": "TYPE_INT8", "aiis_type": "Int8Array"},
    TensorProto.UINT16: { "data_type": "TYPE_UINT16", "aiis_type": "Uint16Array"},
    TensorProto.INT16: { "data_type": "TYPE_INT16", "aiis_type": "Int16Array"},
    TensorProto.INT32: { "data_type": "TYPE_INT32", "aiis_type": "Int32Array"},
    TensorProto.INT64: { "data_type": "TYPE_INT64", "aiis_type": "Int64Array"},
    TensorProto.BOOL: { "data_type": "TYPE_BOOL", "aiis_type": "BooleanArray"},
    TensorProto.FLOAT16: { "data_type": "TYPE_FP16", "aiis_type": "Float16Array"},
    TensorProto.BFLOAT16: { },
    TensorProto.DOUBLE: { "data_type": "TYPE_FP64", "aiis_type": "Float64Array"},
    TensorProto.COMPLEX64: { },
    TensorProto.COMPLEX128: { },
    TensorProto.UINT32: { "data_type": "TYPE_UINT32", "aiis_type": "Uint32Array"},
    TensorProto.UINT64: { "data_type": "TYPE_UINT64", "aiis_type": "Uint64Array"},
    TensorProto.STRING: { "data_type": "TYPE_STRING", "aiis_type": "StringArray"},
    TensorProto.FLOAT8E4M3FN: { },
    TensorProto.FLOAT8E4M3FNUZ: { },
    TensorProto.FLOAT8E5M2: { },
    TensorProto.FLOAT8E5M2FNUZ: { },
    TensorProto.UNDEFINED: { },
}

def get_data_type(tensor_proto):
    data_type = tensor_type_dict.get(tensor_proto, {}).get("data_type", None)
    if data_type is None:
        raise ValueError(f"Unsupported data type: {tensor_proto}")
    return data_type

def get_aiis_type(tensor_proto):
    aiis_type = tensor_type_dict.get(tensor_proto, {}).get("aiis_type", None)
    if aiis_type is None:
        raise ValueError(f"Unsupported data type: {tensor_proto}")
    return aiis_type

TPL_TENSORRT_ACCELERATOR = """
optimization {{
    execution_accelerators {{
        gpu_execution_accelerator : [
            {{
                name : "tensorrt"
                {extra_parameters}
            }}
        ]
    }}
}}
"""


class TensorRTOptimization:
    """
    Class representing TensorRT optimization configuration.

    This class provides methods to configure the optimization parameters for TensorRT.

    Attributes:
        allowed_parameters (list): List of allowed parameter names.
        parameters (dict): Dictionary containing the optimization parameters.

    Methods:
        add_extra_parameter(self, key: str, value: str)
            Adds an extra parameter to the TensorRT optimization.
            allowed_parameters: "precision_mode", "trt_engine_cache_enable", "trt_engine_cache_path",
                                "max_cached_engines", "minimum_segment_size", "max_workspace_size_bytes"

    Intended usage:
        gpu_accelerator = TensorRTOptimization(precision_mode = TensorRTOptimization.PrecisionMode.FP16)
                                    .add_extra_parameter("minimum_segment_size", 3)
        model_config = ModelConfig(model_config, max_batch_size = 1, optimization = gpu_accelerator)
    """

    class PrecisionMode(Enum):
        """
        Enum class for different precision modes in TensorRT optimization.
        """
        FP32 = "FP32"
        FP16 = "FP16"

    allowed_parameters = ["precision_mode",
                          "max_cached_engines", "minimum_segment_size", "max_workspace_size_bytes",
                          "trt_engine_cache_enable", "trt_engine_cache_path"
                          ]

    def __init__(self,
                 precision_mode: PrecisionMode = PrecisionMode.FP32):
        """
        Initializes a new instance of the TensorRTOptimization class.

        Args:
            precision_mode (PrecisionMode): The precision mode for the TensorRT optimization.
        """
        self.parameters = {
            "precision_mode": precision_mode.value,
            "trt_engine_cache_enable": "true",
            "trt_engine_cache_path": "/tmp/triton"
        }

    def add_extra_parameter(self, key: str, value: str):
        """
        Add extra parameter to the TensorRT optimization.

        Args:
            key (str): The key of the parameter.
            value (str): The value of the parameter.
        """
        assert key in self.allowed_parameters, f"Parameter '{key}' is not allowed"
        if key in self.parameters:
            _logger.warn(f"Parameter '{key}' already exists with value {self.parameters[key]} and will be overwritten with value {value}")

        self.parameters[key] = value
        return self

    def __str__(self):
        """
        Returns a string representation of the TensorRTOptimization object.
        """
        return TPL_TENSORRT_ACCELERATOR.format(extra_parameters=self._parameters_to_string())

    def _parameters_to_string(self):
        """
        Converts the parameters dictionary to a string representation.
        """
        return "\n\t\t".join([f"parameters {{ key: \"{key}\" value: \"{value}\" }}" for key, value in self.parameters.items()])


class Warmup(Enum):
    DISABLED = 0
    ZERO_DATA = 1
    RANDOM_DATA = 2

def _warmup_str(warmup):
    if Warmup.ZERO_DATA == warmup:
        return "zero_data: true"
    if Warmup.RANDOM_DATA == warmup:
        return "random_data: true"
    return ""

def _var_to_string(var) -> str:
    return f"""{{
  name: "{var['name']}"
  data_type: {var['data_type']}
  dims: {var['dims']}
}}"""

def _warmup_var_to_string(var, warmup) -> str:
    return f"""\
{{
    key: "{var['name']}"
    value: {{
        data_type: {var['data_type']}
        dims: {var['dims']}
    {_warmup_str(warmup)}
    }}
}}"""


class ModelConfig:
    def __init__(self, onnx_path: Union[str, os.PathLike], max_batch_size: int = 0,
                 warmup: Warmup = Warmup.ZERO_DATA,
                 optimization: Optional[TensorRTOptimization] = None):

        if onnx_path is None or "" == onnx_path:
            raise AssertionError("ONNX model path must not be empty")

        model = load(onnx_path)

        if not warmup:
            self.warmup = Warmup.DISABLED
        else:
            self.warmup = warmup

        self.optimization = optimization

        self.max_batch_size = max_batch_size
        dims_from = 1 if self.max_batch_size > 1 else 0

        self.inputs = []
        self.outputs = []
        for input in model.graph.input:
            tensor = input.type.tensor_type
            self.inputs.append({
                "name": input.name,
                "type": get_aiis_type(tensor.elem_type),
                "data_type": get_data_type(tensor.elem_type),
                "dims": [k.dim_value for k in tensor.shape.dim[dims_from:]],
            })
            if self.max_batch_size > 1 and self.max_batch_size > tensor.shape.dim[0].dim_value:
                _logger.warning(f"max_batch_size is greater than dim[0] of input '{input.name}'")

        for output in model.graph.output:
            tensor = output.type.tensor_type
            self.outputs.append({
                "name": output.name,
                "type": get_aiis_type(tensor.elem_type),
                "data_type": get_data_type(tensor.elem_type),
                "dims": [k.dim_value for k in tensor.shape.dim[dims_from:]],
            })

    def __str__(self):
        input = ", ".join([_var_to_string(input) for input in self.inputs])
        output = ", ".join([_var_to_string(output) for output in self.outputs])

        warmup = ""
        if self.warmup is not Warmup.DISABLED:
            warmup_inputs = ", ".join([_warmup_var_to_string(input, self.warmup) for input in self.inputs])
            warmup = f"""\
model_warmup [{{
  batch_size: 1
  inputs {warmup_inputs}
}}]
"""
        mbs = f"max_batch_size: {self.max_batch_size}" if 1 < self.max_batch_size else ""
        return f"""\
platform: "onnxruntime_onnx"
{mbs}
input [{input}]
output [{output}]
{warmup}
{"" if self.optimization is None else self.optimization.__str__()}
"""

    def __repr__(self):
        return self.__str__()

