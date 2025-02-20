import sys
import os
import glob
import argparse

from validate_json import validate_json, get_schema, write_to_file, get_hash
from create_cpp import create_rixmsg_cpp

ROOT = os.getenv("HOME")
USAGE = """rixmsg [-h] function [arg]

Functions:
  show <rixmsg>          - Show the definition file for a RIX message
  packages               - List all installed packages
  package <package name> - Show all messages names contained within a package
  create <path>          - Create implementation files from RIX message 
                           definition files
"""

def show(rixmsg):
    package, msg = rixmsg.split('/')

    filepath = f'{ROOT}/.rix/rixmsg/defs/{package}/{msg}.json'
    if not os.path.exists(filepath):
        print(f'Error: Package {package} does not exist')
        sys.exit(1)

    with open(filepath, 'r') as file:
        print(file.read())

def list_packages():
    packages = os.listdir(f'{ROOT}/.rix/rixmsg/defs/')
    for package in packages:
        print(package)

def show_package(package):
    package = package.lower()
    package_path =f'{ROOT}/.rix/rixmsg/defs/{package}'

    if not os.path.isdir(package_path):
        print(f'Error: Package {package} does not exist')
        sys.exit(1)

    msgs = os.listdir(package_path)
    for msg in msgs:
        print(msg.split('.')[0])

def create(input_path: str) -> None:
    # Get the schema for validation
    schema = get_schema(f"{ROOT}/.rix/rixmsg/schema/rixmsg.json")

    # Get a list of XML elements
    json_elements = []
    if os.path.isfile(input_path):
        json_elements.append(validate_json(input_path, schema))
    elif os.path.isdir(input_path):
        for json_file in glob.glob(os.path.join(input_path, '*.json')):
            json_elements.append(validate_json(json_file, schema))
    else:
        print(f"{input_path} is not a valid file or directory.")

    for msg in json_elements:
        # Save the definition file globally
        package_dir = f"{ROOT}/.rix/rixmsg/defs/{msg['package']}/"
        os.makedirs(package_dir, exist_ok=True)
        def_file_path = package_dir + f"{msg['name']}.json"
        write_to_file(def_file_path, msg)

        # Add the hash to the msg
        msg['hash'] = get_hash(msg)
        
        # Generate the C++ implementation files
        dir_name = f"{ROOT}/.rix/include/rix/msg/{msg['package']}/"
        os.makedirs(dir_name, exist_ok=True)
        file_name = dir_name + f"{msg['name']}.hpp"
        with open(file_name, "w") as f:
            f.write(create_rixmsg_cpp(msg))

        # Generate the Python implementation files ...
        # Generate the JavaScript implementation files ...

def main(args):
    if args.function == 'show':
        if not args.arg:
            print("Error: show requires a rixmsg file as an argument. Use -h for help")
            sys.exit(1)
        show(args.arg)
    elif args.function == 'packages':
        list_packages()
    elif args.function == 'package':
        if not args.arg:
            print("Error: package requires a package name as an argument. Use -h for help")
            sys.exit(1)
        show_package(args.arg)
    elif args.function == 'create':
        if not args.arg:
            print("Error: create requires a path as an argument. Use -h for help")
            sys.exit(1)
        create(args.arg)
    else:
        print(f'Error: Unknown function {args.function}. Use -h for help')
        sys.exit(1)
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='rixmsg command line tool', usage=USAGE)
    parser.add_argument('-v', '--version', action='version', version='rixmsg 1.0')
    parser.add_argument('function', type=str, help='Function to call (show, packages, package, create)')
    parser.add_argument('arg', type=str, nargs='?', help='Argument for the function')
    args = parser.parse_args()
    
    main(args)