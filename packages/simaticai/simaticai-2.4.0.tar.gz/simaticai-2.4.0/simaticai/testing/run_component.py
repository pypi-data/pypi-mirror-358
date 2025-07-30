# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

"""
Utility script for running an `entrypoint` Python script in a given virtual Python environment.
It is designed to be executed from `simaticai.testing.PipelineRunner` class.
It consumes input data from a joblib file and produces output data into a joblib file.
"""

import os
import sys
import json
import argparse
import joblib
import logging
import importlib
import importlib.metadata
import inspect
from pathlib import Path

logging.basicConfig()
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)


def warn_about_unusued_dependencies(requirements_list):
    """
    Raises a warning if some declared dependencies were not used during test execution

    This method compares the imported modules after test execution with the
    dependency list in the package's requirements.txt file. If the requirements
    contains more than what is required for execution, it raises a warning.
    Also warns the user if the `sqlite3` module is in use, because the current AI Inference Server
    does not support it. A third party replacement library can be used instead.
    """
    imported_packages = []
    packages = importlib.metadata.packages_distributions()
    for key, _ in sys.modules.items():
        if key in packages:
            pkgs = packages.get(key)
            for pkg in pkgs:
                imported_packages.append(pkg)

    imported_packages = set([pkg.replace('-','_').lower() for pkg in imported_packages])
    requirements_list = set([pkg.replace('-','_').lower() for pkg in requirements_list])

    diff = requirements_list.difference(imported_packages)

    if 0 < len(diff):
        _logger.warning(f"WARNING! The following dependencies were not used during execution: {', '.join(diff)}. Consider removing them from the pipeline package.")

    if 'sqlite3' in sys.modules:
        _logger.warning("WARNING! sqlite3 is not part of AI Inference Server's Python runtime. Make sure to include a third party replacement library for sqlite3 in your pipeline package.")

def main(args: argparse.Namespace) -> int:
    """
    Feeds input to the entrypoint and captures output.

    Imports entrypoint module given with its name, and triggers its `run(...)` function with the prepared data in the input file.
    If pipeline_parameters dictionary is not empty, before triggering `run(..)` method, the `update_parameters(..)` method of entrypoint will be called with the dictionary.
    The input file must be a joblib dump, and the joblib must be a dictionary or list of dictionaries.
    One dictionary represents one input for the component with the required variable names and values, which is directly passed to `run()`.
    The output file is a dumped joblib result which is a list containing outputs of the component, in the structure returned from `run()`.

    Args:
        module_name (str): Name of the entrypoint Python script
        input_file (os.Pathlike): Path of the joblib file containing the input payloads
        output_file (os.Pathlike): Path of the joblib file where the outputs will be stored
        pipeline-parameters (json-string): json formatted dictionary defining configurable parameters with their names as key and their values
    """
    entrypoint = importlib.import_module(args.module_name)
    trigger_method = None

    try:
        inspect.signature(entrypoint.process_input)
        trigger_method = "process_input"
    except AttributeError:
        try:
            inspect.signature(entrypoint.run)
            trigger_method = "run"
        except AttributeError:
            _logger.warning("Method run not found")

    if trigger_method is None:
        raise RuntimeError("Neither 'run(data: str)' nor 'process_input(data: dict)' entrypoint method can be found.")

    # configure Pipeline parameters
    if args.pipeline_parameters is not None and args.pipeline_parameters != "{}":
        _logger.debug(f"Calling `update_parameters(..)` with: {args.pipeline_parameters}")
        entrypoint.update_parameters(json.loads(args.pipeline_parameters))

    input_list = joblib.load(args.input_file)
    if not isinstance(input_list, list):
        raise ValueError("Component input must be supplied as a list.")

    if trigger_method == "process_input":
        _logger.debug("Calling `process_input(..)`")
    else:
        _logger.debug("Calling `run(..)`")

    output_list = []
    for input_data in input_list:
        if trigger_method == "process_input":
            output_list.append(entrypoint.process_input(input_data))
        else:
            output_list.append(entrypoint.run(json.dumps(input_data)))

    if args.requirements_file is not None:
        requirements_list = Path(args.requirements_file).read_text().split('#')
        warn_about_unusued_dependencies(requirements_list)

    joblib.dump(output_list, args.output_file)

    if trigger_method == "process_input":
        return 0
    else:
        _logger.warning("Trigger method `run(data: str)` is deprecated and will be removed in the future. Please refer the user manual.")
        return 0b10001  # binary return code means deprecated run method was triggered

if __name__ == '__main__':

    _parser = argparse.ArgumentParser()
    _parser.add_argument("-m", "--module-name", type=str, help="The module which is implemented in the entrypoint Python script.")
    _parser.add_argument("-i", "--input-file", type=str, help="The file which contains input data to test with component.")
    _parser.add_argument("-o", "--output-file", type=str, help="The file which contains calculated output data.")
    _parser.add_argument("-ll", "--log-level", default="INFO", type=str, help="Log Level using `logging` class' enum values.")
    _parser.add_argument("-p", "--pipeline-parameters", type=str, help="Dict of configurable parameters with their values")
    _parser.add_argument("-r", "--requirements-file", type=str, help="The file which contains the required dependencies.")

    _args = _parser.parse_args()

    _logger.setLevel(logging.getLevelName(_args.log_level))

    _logger.info(f"workdir:   {os.path.abspath('.')}")
    _logger.info(f"arguments: {_args}")

    sys.exit(main(_args))
