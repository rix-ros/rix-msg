#!/usr/bin/env python3

import re
import argparse
import os
import hashlib

types = {"char", "int8_t", "int16_t", "int32_t", "int64_t", "uint8_t", "uint16_t", "uint32_t", "uint64_t", "float", "double", "bool" }
sizes = {"char": 1, "int8_t": 1, "int16_t": 2, "int32_t": 4, "int64_t": 8, "uint8_t": 1, "uint16_t": 2, "uint32_t": 4, "uint64_t": 8, "float": 4, "double": 8, "bool": 1 }

def parse_message_definition(in_dir, out_dir):
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

        # Copy .rixmsg file to <out_dir>/defs/<package>/
        if package:
            newDir = out_dir + 'defs/' + package + '/'
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
            fields = re.findall(r'((?:\w+::)?\w+)\s+(\w+)(\[\w+\])?(\[\w+\])?;', match[1])

            if package and message_name and fields:
                msgs[package].append((message_name, fields, template, hashValue))

    return msgs

def getHash(content):
    # Return two 64-bit unsigned integers that reperesent the upper and lower half of an md5 hash
    md5Hash = hashlib.md5(content.encode()).digest()
    hash1 = int.from_bytes(md5Hash[:8], byteorder='big', signed=False)
    hash2 = int.from_bytes(md5Hash[8:], byteorder='big', signed=False)
    return (hash1, hash2)


def generate_headers(dir, msgs):
    if dir[-1] != '/':
        dir += '/'

    for package in msgs:
        newDir = dir + package + '/'
        os.makedirs(newDir, exist_ok=True)

        for msg in msgs[package]:
            message_name = msg[0]
            fields = msg[1]
            template = msg[2]
            hashValue = msg[3]

            filename = newDir + message_name.lower() + '.hpp'
            with open(filename, 'w') as file:
                file.write(f'#pragma once\n\n')
                file.write("#include \"sys/types.h\"\n\n")
                file.write("#include <string>\n")
                file.write("#include <memory>\n")
                file.write("#include <ostream>\n\n")

                file.write("#include \"rix/msg/common.hpp\"\n")
                for field in fields:
                    fieldType = field[0]
                    if "::" in fieldType:
                        other_package = fieldType.split("::")[0]
                        fieldType = fieldType.split("::")[1]
                        file.write(f'#include "rix/msg/{other_package}/{fieldType.lower()}.hpp"\n')
                    elif fieldType not in types:
                            raise Exception(f"Unknown type {fieldType}")

                file.write(f'\nnamespace rix {{\n')
                file.write(f'namespace msg {{\n')
                file.write(f'namespace {package} {{\n\n')

                if template:
                    file.write("template <" + ', '.join([f'{t[0]} {t[1]}' for t in template]) + '>\n')

                file.write(f'class {message_name} {{\n')
                file.write(f'private:\n')

                # Template parameters
                if template:
                    for t in template:
                        file.write(f'    const {t[0]} {t[1].lower()};\n')

                # Hash
                file.write(f'    const Hash _hash;\n')
                file.write('public:\n')

                # Fields
                for field in fields:
                    if field[2]:
                        file.write(f'    {field[0]} {field[1]}{field[2]}{field[3]};\n')
                    else:
                        file.write(f'    {field[0]} {field[1]};\n')
                
                # Constructor
                file.write(f'\n    {message_name}() : ')
                if template:
                    for t in template:
                        file.write(f'{t[1].lower()}({t[1]}), ')
                file.write(f'_hash({message_name}::hash()) {{}}\n\n')

                # Assignment Operator
                file.write(f'    {message_name}& operator=(const {message_name}& other) {{\n')
                file.write(f'        if (this != &other) {{\n')
                for field in fields:
                    if field[2]:
                        file.write(f'            std::memcpy({field[1]}, other.{field[1]}, sizeof({field[1]}));\n')
                    else:
                        file.write(f'            {field[1]} = other.{field[1]};\n')
                file.write(f'        }}\n')
                file.write(f'        return *this;\n')
                file.write(f'    }}\n\n')

                # Copy Constructor
                file.write(f'    {message_name}(const {message_name}& other) : ')
                file.write(f'_hash({message_name}::hash()) {{\n')
                for field in fields:
                    if field[2]:
                        file.write(f'        std::memcpy({field[1]}, other.{field[1]}, sizeof({field[1]}));\n')
                    else:
                        file.write(f'        {field[1]} = other.{field[1]};\n')
                file.write(f'    }}\n\n')

                # Destructor (default)
                file.write(f'    ~{message_name}() = default;\n\n')

                # Size
                if template:
                    file.write(f'    static inline uint32_t size() {{ return sizeof({message_name}<{", ".join(t[1] for t in template)}>); }}\n\n')
                else:
                    file.write(f'    static inline uint32_t size() {{ return sizeof({message_name}); }}\n\n')

                # Decode
                file.write(f'    static const {message_name}* decode(const void *msg, size_t size) {{\n')
                file.write(f'        if (size != {message_name}::size()) {{\n')
                file.write(f'            return nullptr;\n')
                file.write(f'        }}\n')
                file.write(f'        const {message_name} *{message_name.lower()}Msg = static_cast<const {message_name}*>(msg);\n')
                if template:
                    file.write("        if (")
                    for t in template:
                        file.write(f"{message_name.lower()}Msg->{t[1].lower()} != {t[1]} || ")
                    file.write(f"{message_name.lower()}Msg->_hash != {message_name}::hash()) {{\n")
                else:
                    file.write(f'        if ({message_name.lower()}Msg->_hash != {message_name}::hash()) {{\n')
                file.write(f'            return nullptr;\n')
                file.write(f'        }}\n')
                file.write(f'        return {message_name.lower()}Msg;\n')
                file.write(f'    }}\n\n')

                # Encode
                file.write(f'    static const void* encode(const {message_name} *msg) {{\n')
                file.write(f'        return static_cast<const void*>(msg);\n')
                file.write(f'    }}\n\n')

                # Def
                file.write(f'    static std::string def()\n')
                file.write(f'    {{\n')
                file.write(f'        return "{message_name} {{\\n')
                for field in fields:
                    file.write(f'    {field[0]} {field[1]}{field[2]}{field[3]};\\n')
                file.write(f'    }}";\n')
                file.write(f'    }}\n\n')

                # Hash
                file.write(f'    static inline Hash hash() {{\n')
                file.write(f'        return Hash({hashValue[0]}ULL, {hashValue[1]}ULL);\n')
                file.write(f'    }}\n\n')

                # Operator<<
                file.write(f'    friend std::ostream &operator<<(std::ostream &os, const {message_name} &{message_name.lower()}Msg) {{\n')
                file.write(f'        os << "{message_name} {{\\n";\n')
                for field in fields:
                    # If the field is an array or an array of strings, we need to iterate over it
                    if (field[2] and field[0] != 'char') or (field[3] and field[0] == 'char'):
                        file.write(f'        os << "{field[1]}: ";\n')
                        file.write(f'        for (const auto &item : {message_name.lower()}Msg.{field[1]}) {{\n')
                        file.write(f'            os << item << ", ";\n')
                        file.write(f'        }}\n')
                        file.write(f'        os << "\\n";\n')
                    # If the field is a double array, we need to iterate over it
                    elif field[3]:
                        file.write(f'        os << "{field[1]}: ";\n')
                        file.write(f'        for (const auto &row : {message_name.lower()}Msg.{field[1]}) {{\n')
                        file.write(f'            for (const auto &item : row) {{\n')
                        file.write(f'                os << item << ", ";\n')
                        file.write(f'            }}\n')
                        file.write(f'            os << "\\n";\n')
                        file.write(f'        }}\n')
                    else:
                        file.write(f'        os << "{field[1]}: " << {message_name.lower()}Msg.{field[1]} << "\\n";\n')
                file.write(f'        os << "}}";\n')
                file.write(f'        return os;\n')
                file.write(f'    }}\n')
                file.write(f'}};\n\n')
                file.write(f"}} // namespace {package}\n")
                file.write("} // namespace msg\n")
                file.write("} // namespace rix\n")
            
def main():
    parser = argparse.ArgumentParser(description='Generate C++ header file from message definition')
    parser.add_argument('in_dir', type=str, help='Message definition file')
    parser.add_argument('-o', '--out_dir', type=str, help='Output directory', default="/usr/local/include/rix/msg/")
    args = parser.parse_args()

    msgs = parse_message_definition(args.in_dir, args.out_dir)
    generate_headers(args.out_dir, msgs)


if __name__ == '__main__':
    main()