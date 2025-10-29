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
    Json,
)
from message import Message
from create_cpp import create_rixmsg_cpp
from create_js import create_rixmsg_js
from create_py import create_rixmsg_py

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
    Writes the index file for all of the current RIX message definitions in ~/.rix/rixmsg/defs sorted by hash.
    Format: <hash> <package>/<message>
    """
    index_file = f"{ROOT}/.rix/rixmsg/index.txt"
    hashes_sorted: list[str] = []
    hash_to_msg: dict[str, str] = {}

    # For each package in defs, for each message in the package, read the hash and store it in a list
    for package in os.listdir(f"{ROOT}/.rix/rixmsg/defs/"):
        package_path = f"{ROOT}/.rix/rixmsg/defs/{package}"
        for msg in os.listdir(package_path):
            if msg.endswith(".json"):
                msg_data = get_dict_from_json(f"{package_path}/{msg}")
                hash_value = str(msg_data["hash"])
                hashes_sorted.append(hash_value)
                hash_to_msg[hash_value] = f"{package}/{msg[:-5]}"  # Remove '.json'

    # Sort the hashes and write to the index file
    hashes_sorted = sorted(hashes_sorted)
    with open(index_file, "w") as f:
        for hash_value in hashes_sorted:
            f.write(f"{hash_value} {hash_to_msg[hash_value]}\n")


def show(rixmsg: str) -> None:
    """
    Show the definition file for a RIX message.
    """
    # Format: package/message (e.g. standard/Header)
    package, msg = rixmsg.split("/")
    filepath = f"{ROOT}/.rix/rixmsg/defs/{package}/{msg}.json"
    if not os.path.exists(filepath):
        print(f"Error: Package {package} does not exist")
        sys.exit(1)

    with open(filepath, "r") as file:
        # Print the contents of the file
        print(file.read())


def list_packages() -> None:
    """
    List all installed packages.
    """
    # List all packages in ~/.rix/rixmsg/defs
    packages = os.listdir(f"{ROOT}/.rix/rixmsg/defs/")
    for package in packages:
        print(package)


def show_package(package: str) -> None:
    """
    Show all messages names contained within a package.
    """
    package = package.lower()
    package_path = f"{ROOT}/.rix/rixmsg/defs/{package}"

    if not os.path.isdir(package_path):
        print(f"Error: Package {package} does not exist")
        sys.exit(1)

    # List all messages in the package
    msgs = os.listdir(package_path)
    for msg in msgs:
        print(msg.split(".")[0])


def validate(input_path: str) -> None:
    """
    Validate a RIX message JSON file against the RIX message schema.
    """
    # Get the schema for validation
    schema = get_schema(f"{ROOT}/.rix/rixmsg/schema.json")

    # Check if the input path is a file
    if os.path.isfile(input_path):
        # Validate the file
        if validate_json(input_path, schema) is not None:
            print(f"{input_path} is a valid RIX message.")
        else:
            print(f"{input_path} is invalid.")
    else:
        print(f"{input_path} is not a file.")


def create(input_path: str) -> None:
    """
    Create implementation files from RIX message definition files.
    The input path can be a single JSON file or a directory containing multiple JSON files.
    """
    # Get the schema for validation
    schema = get_schema(f"{ROOT}/.rix/rixmsg/schema.json")

    # Get a list of JSON elements
    json_elements: list[Json] = []

    # If the input path is a file, validate it and add it to the list
    if os.path.isfile(input_path):

        # Validate the file
        msg = validate_json(input_path, schema)
        if msg is None:
            sys.exit(1)

        # If there is no hash defined, create one
        if "hash" not in msg:
            msg["hash"] = get_hash(input_path)

        json_elements.append(msg)

    # If the input path is a directory, validate all JSON files in the directory and add them to the list
    elif os.path.isdir(input_path):
        for json_file in glob.glob(os.path.join(input_path, "*.json")):

            # Validate the file
            msg = validate_json(json_file, schema)
            if msg is None:
                sys.exit(1)

            # If there is no hash defined, create one
            if "hash" not in msg:
                msg["hash"] = get_hash(json_file)

            json_elements.append(msg)
    else:
        print(f"{input_path} is not a valid file or directory.")

    for msg_json in json_elements:
        # Save the definition file globally
        package_dir = f"{ROOT}/.rix/rixmsg/defs/{msg_json['package']}/"
        os.makedirs(package_dir, exist_ok=True)
        def_file_path = package_dir + f"{msg_json['name']}.json"
        write_to_file(def_file_path, msg_json)

        msg = Message(
            msg_json["name"], msg_json["package"], msg_json["hash"], msg_json["fields"]
        )

        # Generate the C++ implementation files
        dir_name = f"{ROOT}/.rix/include/rix/{msg.package}/"
        os.makedirs(dir_name, exist_ok=True)
        file_name = dir_name + f"{msg.name}.hpp"
        with open(file_name, "w") as f:
            f.write(create_rixmsg_cpp(msg))

        # # Generate the JavaScript implementation files
        # dir_name = f"{ROOT}/.rix/js/rixmsg/{msg.package}/"
        # os.makedirs(dir_name, exist_ok=True)
        # file_name = dir_name + f"{msg.name}.js"
        # with open(file_name, "w") as f:
        #     f.write(create_rixmsg_js(msg))

        # # Generate the Python implementation files
        # dir_name = f"{ROOT}/.rix/python/rix/rix/msg/{msg.package}/"
        # os.makedirs(dir_name, exist_ok=True)
        # file_name = dir_name + f"{msg.name}.py"
        # with open(file_name, "w") as f:
        #     f.write(create_rixmsg_py(msg))

        # # Create the __init__.py file
        # file_name = dir_name + "__init__.py"
        # with open(file_name, "w") as f:
        #     # For each message in the package, import it
        #     for msg_in_pkg in os.listdir(package_dir):
        #         if msg_in_pkg.endswith(".json"):
        #             message_name = msg_in_pkg[:-5]  # Remove '.json'
        #             f.write(f"from .{message_name} import {message_name}\n")

    # Re-index the definitions
    index()


def main(args: argparse.Namespace):
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
    parser = argparse.ArgumentParser(description="rixmsg CLI", usage=USAGE)
    parser.add_argument("-v", "--version", action="version", version="rixmsg 1.0")
    parser.add_argument(
        "function", type=str, help="Function to call (show, packages, package, create)"
    )
    parser.add_argument("arg", type=str, nargs="?", help="Argument for the function")
    args = parser.parse_args()

    main(args)
