# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

"""
AI Software Development Kit CLI
"""

import argparse

from simaticai import deployment

argparser = argparse.ArgumentParser(prog='python -m simaticai', description="AI SDK command line interface.", add_help=True)
cmd_parsers = argparser.add_subparsers(dest='command')

parser_convert_package = cmd_parsers.add_parser('convert_package', help="Convert a Pipeline Configuration Package to an Edge Configuration Package that can be directly deployed.")
parser_convert_package.add_argument('package_zip', help="""Path to the input package file.
For "{path}/{name}_{version}.zip", the output file will be created as "{path}/{name}-edge_{version}.zip".
If a file with such a name already exists, it is overwritten.""")

parser_delta_package = cmd_parsers.add_parser('create_delta_package', help="Create a Delta Configuration Package that can be deployed onto the original pipeline on AI Inference Server.")
parser_delta_package.add_argument('origin_package', help="Path to Origin Edge Package file.")
parser_delta_package.add_argument('new_package', help="Path to New Edge Package file.")


args = argparser.parse_args()

if args.command == "convert_package":
    target_zip = deployment.convert_package(args.package_zip)
    print(f"Package successfully converted and saved as '{target_zip}'")

elif args.command == "create_delta_package":
    target_zip = deployment.create_delta_package(args.origin_package, args.new_package)
    print(f"Delta package successfully created and saved as '{target_zip}'")
else:
    argparser.error("No subcommand selected.")
