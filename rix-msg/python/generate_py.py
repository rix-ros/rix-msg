import os
from common import types

ctypes_format_chars = {"char": "c_char", "int8_t": "c_int8", "int16_t": "c_int16", "int32_t": "c_int32", "int64_t": "c_int64", "uint8_t": "c_uint8", "uint16_t": "c_uint16", "uint32_t": "c_uint32", "uint64_t": "c_uint64", "float": "c_float", "double": "c_double", "bool": "c_bool" }
python_types = {"char": "int", "int8_t": "int", "int16_t": "int", "int32_t": "int", "int64_t": "int", "uint8_t": "int", "uint16_t": "int", "uint32_t": "int", "uint64_t": "int", "float": "float", "double": "float", "bool": "bool" }

def generate_py(dir, msgs):
    if dir[-1] != '/':
        dir += '/'

    os.makedirs(dir + 'rixmsg/', exist_ok=True)
    with open(dir + 'rixmsg/__init__.py', 'w') as file:
        file.write('')

    for package in msgs:
        newDir = dir + 'rixmsg/' + package + '/'
        os.makedirs(newDir, exist_ok=True)
        with open(newDir + '__init__.py', 'w') as file:
            file.write('')

        for msg in msgs[package]:
            message_name = msg[0]
            fields = msg[1]
            template = msg[2]
            hashValue = msg[3]
            filename = newDir + message_name + '.py'

            with open(filename, 'w') as file:
                file.write(f'import ctypes\n')

                include_set = set()
                for field in fields:
                    fieldType = field[0]
                    if "::" in fieldType:
                        other_package, field_type = fieldType.split("::")
                        include_file = field_type
                        if include_file not in include_set:
                            include_set.add(include_file)
                            file.write(f'from rixmsg.{other_package}.{include_file} import {field_type}\n')
                    elif fieldType not in types:
                            raise Exception(f"Unknown type {fieldType}")
                
                spacing = ""
                if template:
                    file.write(f'from typing import Type\n')
                    file.write(f'\ndef {message_name}Template(')
                    file.write(', '.join([f'{t[1]}: {python_types[t[0]]}' for t in template]))
                    file.write(f') -> Type[\'{message_name}\']:')
                    spacing = "    "

                file.write(f'\n{spacing}class {message_name}(ctypes.Structure):\n')
                file.write(f'    {spacing}_pack_ = 1\n')
                file.write(f'    {spacing}_fields_ = [\n')
                for field in fields:
                    is_array = field[2] or field[3]
                    is_double_array = field[3]
                    is_nested = "::" in field[0]
                    if is_array:
                        has_template = False
                        try:
                            size1 = int(field[2][1:-1])
                        except ValueError:
                            size1 = field[2][1:-1]
                            has_template = True
                        try:
                            size2 = int(field[3][1:-1]) if is_double_array else 1
                        except ValueError:
                            size2 = field[3][1:-1] if is_double_array else 1
                            has_template = True

                        if is_nested and has_template:
                            typeName = field[0].split("::")[1]
                            file.write(f'        {spacing}("{field[1]}", {typeName} * {size1} * {size2}),\n')
                        elif is_nested:
                            typeName = field[0].split("::")[1]
                            file.write(f'        {spacing}("{field[1]}", {typeName} * {size1 * size2}),\n')
                        elif has_template:
                            file.write(f'        {spacing}("{field[1]}", ctypes.{ctypes_format_chars[field[0]]} * {size1} * {size2}),\n')
                        else:
                            file.write(f'        {spacing}("{field[1]}", ctypes.{ctypes_format_chars[field[0]]} * {size1 * size2}),\n')
                    elif is_nested:
                        typeName = field[0].split("::")[1]
                        file.write(f'        {spacing}("{field[1]}", {typeName}),\n')
                    else:
                        file.write(f'        {spacing}("{field[1]}", ctypes.{ctypes_format_chars[field[0]]}),\n')
                file.write(f'    {spacing}]\n\n')

                # Constructor
                file.write(f'    {spacing}def __init__(self):\n')
                file.write(f'        {spacing}super({message_name}, self).__init__()\n\n')

                # Encode
                file.write(f'    {spacing}def encode(self) -> bytes:\n')
                file.write(f'        {spacing}return ctypes.string_at(ctypes.addressof(self), ctypes.sizeof(self))\n\n')

                # Decode
                file.write(f'    {spacing}@staticmethod\n')
                file.write(f'    {spacing}def decode(msg: bytes) -> \'{message_name}\':\n')
                file.write(f'        {spacing}if len(msg) != {message_name}.size():\n')
                file.write(f'            {spacing}return None\n')
                file.write(f'        {spacing}return {message_name}.from_buffer_copy(msg)\n\n')

                # Size
                file.write(f'    {spacing}@staticmethod\n')
                file.write(f'    {spacing}def size():\n')
                file.write(f'        {spacing}return ctypes.sizeof({message_name})\n\n')

                # Hash
                file.write(f'    {spacing}@staticmethod\n')
                file.write(f'    {spacing}def hash() -> tuple:\n')
                file.write(f'        {spacing}return ({hashValue[0]}, {hashValue[1]})\n')

                if template:
                    file.write(f'\n    return {message_name}\n')

    # packages = [f.path.split('/')[-1] for f in os.scandir(dir) if (f.is_dir() and f.path.split('.')[-1] != 'egg-info' and f.path.split('/')[-1] != 'build')]
    with open(dir + 'setup.py', 'w') as file:
        file.write('from setuptools import setup, find_packages\n\n')
        file.write('setup(\n')
        file.write('    name="rixmsg",\n')
        file.write('    version="1.0.0",\n')
        file.write('    description="Message definitions for RIX",\n')
        file.write('    packages=find_packages(),\n')
        file.write(')\n')