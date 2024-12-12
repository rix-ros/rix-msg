#!/usr/bin/env python3

import argparse
import os
import hashlib
import re
import sys

from generate_cpp import generate_cpp
from generate_js import generate_js
from generate_py import generate_py

ROOT = os.getenv("HOME")

def parse_message_definition(in_dir):
    if in_dir[-1] != '/':
        in_dir += '/'

    msgs = {}
    for filename in os.listdir(in_dir):
        if not filename.endswith('.rixmsg'):
            continue
        
        content = ""
        with open(in_dir+filename, 'r') as file:
            content = file.read()

        hashValue = getHash(content)

        package_match = re.search(r'package:\s*(\w+);', content)
        package = package_match.group(1) if package_match else None

        if package:
            ROOT = os.getenv("HOME")
            newDir = ROOT + "/.rix/rixmsg/defs/" + package + '/'
            os.makedirs(newDir, exist_ok=True)
            with open(newDir + filename, 'w') as file:
                file.write(content)

        if package not in msgs:
            msgs[package] = []

        template_match = re.findall(r'template:\s*(.*);', content)
        template = []
        if template_match:
            for key, value in [x.split() for x in template_match[0].split(',')]:
                template.append((key, value))
        
        message_match = re.findall(r'(\w+)\s*{\s*([^}]+)\s*}', content)
        for match in message_match:
            message_name = match[0]
            fields = re.findall(r'((?:\w+::)?\w+(?:<[^>]+>)?)\s+(\w+)(\[[^\]]+\])?;', match[1])

            if package and message_name and fields:
                msgs[package].append((message_name, fields, template, hashValue))

    return msgs

def getHash(content):
    # Return two 64-bit unsigned integers that reperesent the upper and lower half of an md5 hash
    md5Hash = hashlib.md5(content.encode()).digest()
    hash1 = int.from_bytes(md5Hash[:8], byteorder='big', signed=False)
    hash2 = int.from_bytes(md5Hash[8:], byteorder='big', signed=False)
    return (hash1, hash2)

def help():
    print("Usage: rixmsg <function> [args]")
    print("")
    print("Functions:")
    print("  help - Print this help message")
    print("  show <rixmsg> - Show the definition of a rixmsg")
    print("  packages - List all packages")
    print("  package <package name> - Show all messages in a package")
    print("  create <path> - Create implementation files from rixmsg files")

def show(rixmsg):
    package, msg = rixmsg.split('/')

    filepath = f'{ROOT}/.rix/rixmsg/defs/{package}/{msg}.rixmsg'
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

def create_headers(path):
    if not os.path.isdir(path):
        print(f'Error: Path {path} does not exist')
        sys.exit(1)

    msgs = parse_message_definition(path)
    generate_cpp(ROOT + "/.rix/include/rix/msg/", msgs)
    os.makedirs(ROOT + "/.rix/node_modules/rixmsg/", exist_ok=True)
    generate_js(ROOT + "/.rix/node_modules/rixmsg/", msgs)
    os.makedirs(ROOT + "/.rix/python/rixmsg/", exist_ok=True)
    generate_py(ROOT + "/.rix/python/rixmsg/", msgs)

def main(args=None):
    parser = argparse.ArgumentParser(description='Generate RIX message implementation files from .rixmsg definition files')
    parser.add_argument('function', type=str, help='Function to call (help, show, packages, package, create)')
    parser.add_argument('arg1', type=str, nargs='?', help='Argument for the function')
    parser.add_argument('in_dir', type=str, help='Message definition file', nargs='?')
    args = parser.parse_args(args)

    if args.function == 'help':
        help()
    elif args.function == 'show':
        if not args.arg1:
            print("Error: show function requires a rixmsg file as an argument")
            print("Usage: rixmsg show <rixmsg>")
            sys.exit(1)
        show(args.arg1)
    elif args.function == 'packages':
        list_packages()
    elif args.function == 'package':
        if not args.arg1:
            print("Error: package function requires a package name as an argument")
            print("Usage: rixmsg package <package name>")
            sys.exit(1)
        show_package(args.arg1)
    elif args.function == 'create':
        if not args.arg1:
            print("Error: create function requires a path as an argument")
            print("Usage: rixmsg create <path>")
            sys.exit(1)
        create_headers(args.arg1)
    else:
        print(f'Error: Unknown function {args.function}')
        help()
        sys.exit(1)

if __name__ == "__main__":
    main()
