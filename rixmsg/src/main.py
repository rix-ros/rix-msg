import sys
import os
import glob
import argparse

from validate_json import (
    validate_json,
    get_schema,
    write_to_file,
    get_hash,
    get_dict_from_json,
)
from type_regex import (
    add_flags_to_fields,
)
from create_cpp import create_rixmsg_cpp
from create_js import create_rixmsg_js
from create_py import create_rixmsg_py
# from create_protobuf import create_rixmsg_protobuf

ROOT = os.getenv("HOME")
USAGE = """rixmsg [-h] function [arg]

Functions:
  show <rixmsg>          - Show the definition file for a RIX message
  packages               - List all installed packages
  package <package name> - Show all messages names contained within a package
  create <path>          - Create implementation files from RIX message 
                           definition files
  index                  - Index the RIX message definitions
  validate <path>        - Validate a RIX message JSON file against the RIX message schema
"""


def index():
    """
    Writes the index file for all of the current RIX message definitions in ~/.rix/rixmsg/defs.
    Sorted by hash.
    Format:
    <hash> <package>/<message>
    """
    index_file = f"{ROOT}/.rix/rixmsg/index.txt"
    hashes_sorted = []
    hash_to_msg = {}
    for package in os.listdir(f"{ROOT}/.rix/rixmsg/defs/"):
        package_path = f"{ROOT}/.rix/rixmsg/defs/{package}"
        for msg in os.listdir(package_path):
            if msg.endswith(".json"):
                msg_data = get_dict_from_json(f"{package_path}/{msg}")
                hash_value = msg_data["hash"]
                hashes_sorted.append(hash_value)
                hash_to_msg[hash_value] = f"{package}/{msg[:-5]}"
    hashes_sorted = sorted(hashes_sorted)
    with open(index_file, "w") as f:
        for hash_value in hashes_sorted:
            f.write(f"{hash_value} {hash_to_msg[hash_value]}\n")


def show(rixmsg):
    package, msg = rixmsg.split("/")

    filepath = f"{ROOT}/.rix/rixmsg/defs/{package}/{msg}.json"
    if not os.path.exists(filepath):
        print(f"Error: Package {package} does not exist")
        sys.exit(1)

    with open(filepath, "r") as file:
        print(file.read())


def list_packages():
    packages = os.listdir(f"{ROOT}/.rix/rixmsg/defs/")
    for package in packages:
        print(package)


def show_package(package):
    package = package.lower()
    package_path = f"{ROOT}/.rix/rixmsg/defs/{package}"

    if not os.path.isdir(package_path):
        print(f"Error: Package {package} does not exist")
        sys.exit(1)

    msgs = os.listdir(package_path)
    for msg in msgs:
        print(msg.split(".")[0])

def validate(input_path: str) -> None:
    schema = get_schema(f"{ROOT}/.rix/rixmsg/schema.json")
    if os.path.isfile(input_path):
        if validate_json(input_path, schema) is not None:
            print(f"{input_path} is a valid RIX message.")
        else:
            print(f"{input_path} is invalid.")
    else: 
        print(f"{input_path} is not a file.")

def create(input_path: str) -> None:
    # Get the schema for validation
    schema = get_schema(f"{ROOT}/.rix/rixmsg/schema.json")

    # Get a list of JSON elements
    json_elements = []
    if os.path.isfile(input_path):
        msg = validate_json(input_path, schema)
        if "hash" not in msg:
            msg["hash"] = get_hash(input_path)
        json_elements.append(msg)
    elif os.path.isdir(input_path):
        for json_file in glob.glob(os.path.join(input_path, "*.json")):
            msg = validate_json(json_file, schema)
            if "hash" not in msg:
                msg["hash"] = get_hash(json_file)
            json_elements.append(msg)
    else:
        print(f"{input_path} is not a valid file or directory.")

    for msg in json_elements:
        # Save the definition file globally
        package_dir = f"{ROOT}/.rix/rixmsg/defs/{msg['package']}/"
        os.makedirs(package_dir, exist_ok=True)
        def_file_path = package_dir + f"{msg['name']}.json"
        write_to_file(def_file_path, msg)

        # Add flags to the fields
        add_flags_to_fields(msg["fields"])

        # Generate the C++ implementation files
        dir_name = f"{ROOT}/.rix/include/rix/msg/{msg['package']}/"
        os.makedirs(dir_name, exist_ok=True)
        file_name = dir_name + f"{msg['name']}.hpp"
        with open(file_name, "w") as f:
            f.write(create_rixmsg_cpp(msg))

        # Generate the JavaScript implementation files
        dir_name = f"{ROOT}/.rix/js/rixmsg/{msg['package']}/"
        os.makedirs(dir_name, exist_ok=True)
        file_name = dir_name + f"{msg['name']}.js"
        with open(file_name, "w") as f:
            f.write(create_rixmsg_js(msg))

        # Generate the Python implementation files
        dir_name = f"{ROOT}/.rix/python/rixmsg/rixmsg/{msg['package']}/"
        os.makedirs(dir_name, exist_ok=True)
        # Create the __init__.py file
        file_name = dir_name + "__init__.py"
        with open(file_name, "w") as f:
            f.write("")
        file_name = dir_name + f"{msg['name']}.py"
        with open(file_name, "w") as f:
            f.write(create_rixmsg_py(msg))

        # # Generate the .proto files
        # dir_name = f"{ROOT}/.rix/protobuf/rixmsg/protobuf/{msg['package']}/"
        # os.makedirs(dir_name, exist_ok=True)
        # file_name = dir_name + f"{msg['name']}.proto"
        # with open(file_name, "w") as f:
        #     f.write(create_rixmsg_protobuf(msg))

        # # Create __init__.py file for the protobuf directory
        # proto_dir_name = f"{ROOT}/.rix/python/rixmsg/rixmsg/protobuf/"
        # os.makedirs(proto_dir_name, exist_ok=True)
        # proto_file_name = proto_dir_name + "__init__.py"
        # with open(proto_file_name, "w") as f:
        #     f.write("")

        # # Create __init__.py file for the package directory
        # package_dir_name = f"{ROOT}/.rix/python/rixmsg/rixmsg/protobuf/{msg['package']}/"
        # os.makedirs(package_dir_name, exist_ok=True)
        # package_file_name = package_dir_name + "__init__.py"
        # with open(package_file_name, "w") as f:
        #     f.write("")

        # # Generate the Protobuf Python implementation files
        # os.system(
        #     f"protoc -I={ROOT}/.rix/protobuf --descriptor_set_out={ROOT}/.rix/python/rixmsg/rixmsg/protobuf/{msg['package']}/{msg['package']}.bin --python_out={ROOT}/.rix/python/rixmsg/ {ROOT}/.rix/protobuf/rixmsg/protobuf/{msg['package']}/*.proto"
        # )

    # Re-index the definitions
    index()


def main(args):
    if args.function == "show":
        if not args.arg:
            print("Error: show requires a rixmsg file as an argument. Use -h for help")
            sys.exit(1)
        show(args.arg)
    elif args.function == "packages":
        list_packages()
    elif args.function == "package":
        if not args.arg:
            print(
                "Error: package requires a package name as an argument. Use -h for help"
            )
            sys.exit(1)
        show_package(args.arg)
    elif args.function == "create":
        if not args.arg:
            print("Error: create requires a path as an argument. Use -h for help")
            sys.exit(1)
        create(args.arg)
    elif args.function == "index":
        index()
    elif args.function == "validate":
        validate(args.arg)
    else:
        print(f"Error: Unknown function {args.function}. Use -h for help")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="rixmsg CLI", usage=USAGE
    )
    parser.add_argument("-v", "--version", action="version", version="rixmsg 1.0")
    parser.add_argument(
        "function", type=str, help="Function to call (show, packages, package, create)"
    )
    parser.add_argument("arg", type=str, nargs="?", help="Argument for the function")
    args = parser.parse_args()

    main(args)
