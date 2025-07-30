# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

"""
Utility script for running an ONNX model in a given virtual Python environment.
It is designed to be executed from `simaticai.testing.PipelineRunner` class.
It consumes input data from a joblib file and produces output data into a joblib file.
"""

import argparse
import joblib
import logging
import numpy
import os
import sys

from onnxruntime import InferenceSession
from google.protobuf import text_format
from google.protobuf import json_format

try:
    import model_config_pb2
except ImportError:
    import simaticai.model_config_pb2 as model_config_pb2  # for documentation build

logging.basicConfig()
_logger = logging.getLogger("simaticai.testing.pipeline_runner.run_gpuruntime_component")
_logger.setLevel(logging.INFO)

def _get_proto_config(config_path):
    """Reads model configuration from config.pbtxt into a dictionary

    Args:
        config_path (os.PathLike): path to `config.pbtxt` file, generally model_path.parents[1] / "config.pbtxt"
    """
    with open(config_path, 'r') as file:
        config_msg = text_format.Parse(file.read(), model_config_pb2.ModelConfig())
        config_dict = json_format.MessageToDict(config_msg)
    return config_dict

def _get_new_shape(config_input, model_input, input_name):
    """Calculates the input shape if it is a batch of data.
    In case of batched input, the number of input arrays must be max_batch_size or less.
    The input shape is a flat array and must be reshaped based on one input shape, and the size of batch can be calculated.

    Args:
        config_input (dict): dictionary with information of the input type and shape from configuration file
        model_input (dict): standard input format for GPU Runtime, the input tensor is flattened into numpy array
        input_name (str): name of the actual model_input to search in config_input
    """
    config_shape = numpy.array([i["dims"] for i in config_input if i["name"] == input_name]).flatten().astype(numpy.int32)
    img_size = config_shape.prod()
    input_size = numpy.prod(model_input.shape)
    batch_size = input_size // img_size

    return numpy.concatenate(([batch_size], config_shape))

def main(model_path, config_path, input_file, output_file):
    """Feeds input to the ML Model saved in ONNX format and captures output.

    Reads the given model and creates an onnxruntime Session to
    The input file must be a joblib dump, and the joblib must be a dictionary or list of dictionaries.
    The output file is a dumped joblib result list containing the input dictionary extended with the generated predictions.

    Args:
        model_path (str): File path for the stored ML Model in ONNX format
        input_file (os.Pathlike): Path of the joblib file containing the input payloads
        output_file (os.Pathlike): Path of the joblib file where the outputs will be stored
    """
    input_list = joblib.load(input_file)
    input_list = input_list if type(input_list) is list else [input_list]

    output_list = input_list.copy()
    session = InferenceSession(model_path)

    model_config = _get_proto_config(config_path)
    max_batch_size = model_config.get("maxBatchSize", 0)

    inputs = [input for input in session.get_inputs()]
    outputs = [output for output in session.get_outputs()]
    predictions = [output.name for output in outputs]

    for _output in output_list:
        _input_tensor = {}
        for _input in inputs:
            if max_batch_size > 0:
                input_shape = _get_new_shape(model_config["input"], _output[_input.name], _input.name)
                if input_shape[0] > max_batch_size:
                    _logger.warning(f"Received input batch size ({input_shape[0]}) is greater than max_batch_size ({max_batch_size})!")
                _input_tensor[_input.name] = _output[_input.name].reshape(input_shape)
            else:
                _input_tensor[_input.name] = _output[_input.name].reshape(_input.shape)

        _predictions = session.run(predictions, _input_tensor)

        for i in range(len(_predictions)):
            _output[predictions[i]] = _predictions[i]

    joblib.dump(output_list, output_file)

    return 0

if __name__ == '__main__':

    _parser = argparse.ArgumentParser()
    _parser.add_argument("-m", "--model-path", type=str, help="The path of ONNX file.")
    _parser.add_argument("-c", "--config-path", type=str, help="The path of config.pbtxt")
    _parser.add_argument("-i", "--input-file", type=str, help="The file which contains input data to test with component.")
    _parser.add_argument("-o", "--output-file", type=str, help="The file which contains calculated output data.")
    _parser.add_argument("-ll", "--log-level", default="INFO", type=str, help="Log Level using `logging` class' enum values.")

    _args = _parser.parse_args()
    _logger.setLevel(logging.getLevelName(_args.log_level))

    _logger.info(f"arguments: \t {_args}")
    _logger.info(f"workdir: \t {os.path.abspath('.')}")

    sys.exit(main(_args.model_path, _args.config_path, _args.input_file, _args.output_file))
