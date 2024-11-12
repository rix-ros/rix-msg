import os
from common import types

def generate_cpp(dir, msgs):
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
            filename = newDir + msg[4] + '.hpp'

            with open(filename, 'w') as file:
                file.write(f'#pragma once\n\n')
                file.write("#include <sys/types.h>\n\n")
                file.write("#include <string>\n")
                file.write("#include <cstring>\n\n")

                file.write("#include \"rix/msg/common.hpp\"\n")

                include_set = set()
                for field in fields:
                    fieldType = field[0]
                    if "::" in fieldType:
                        other_package = fieldType.split("::")[0]
                        fieldType = fieldType.split("::")[1]
                        include_file = f'{other_package}/{fieldType.lower()}'
                        if include_file not in include_set:
                            include_set.add(include_file)
                            file.write(f'#include "rix/msg/{include_file}.hpp"\n')
                    elif fieldType not in types:
                            raise Exception(f"Unknown type {fieldType}")

                file.write(f'\nnamespace rix {{\n')
                file.write(f'namespace msg {{\n')
                file.write(f'namespace {package} {{\n\n')

                if template:
                    file.write("template <" + ', '.join([f'{t[0]} {t[1]}' for t in template]) + '>\n')

                file.write(f'struct {message_name} {{\n')
                file.write(f'private:\n')

                # Fields
                for field in fields:
                    if field[2]:
                        file.write(f'    {field[0]} {field[1]}{field[2]}{field[3]};\n')
                    else:
                        file.write(f'    {field[0]} {field[1]};\n')
                
                # Constructor
                file.write(f'\n    {message_name}() = default;\n')

                # Assignment Operator
                file.write(f'    {message_name}& operator=(const {message_name}& other) {{\n')
                file.write(f'        if (this != &other) {{\n')
                file.write(f'            std::memcpy(this, &other, sizeof({message_name}));\n')
                file.write(f'        }}\n')
                file.write(f'        return *this;\n')
                file.write(f'    }}\n\n')

                # Copy Constructor
                file.write(f'    {message_name}(const {message_name}& other) {{\n')
                file.write(f'        std::memcpy(this, &other, sizeof({message_name}));\n')
                file.write(f'    }}\n\n')

                # Destructor (default)
                file.write(f'    ~{message_name}() = default;\n\n')

                # Size
                if template:
                    file.write(f'    static inline uint32_t size() {{ return sizeof({message_name}<{", ".join(t[1] for t in template)}>); }}\n\n')
                else:
                    file.write(f'    static inline uint32_t size() {{ return sizeof({message_name}); }}\n\n')

                # Decode
                file.write(f'    static const {message_name}* decode(const uint8_t *msg, size_t size) {{\n')
                file.write(f'        if (size != {message_name}::size()) {{\n')
                file.write(f'            return nullptr;\n')
                file.write(f'        }}\n')
                file.write(f'        return reinterpret_cast<const {message_name}*>(msg);\n')
                file.write(f'    }}\n\n')

                # Encode
                file.write(f'    const uint8_t* encode() const {{\n')
                file.write(f'        return reinterpret_cast<const uint8_t*>(this);\n')
                file.write(f'    }}\n\n')

                # Hash
                file.write(f'    static inline Hash hash() {{\n')
                file.write(f'        return Hash({hashValue[0]}ULL, {hashValue[1]}ULL);\n')
                file.write(f'    }}\n\n')

                file.write(f'}};\n\n')
                file.write(f'}} // namespace {package}\n')
                file.write("} // namespace msg\n")
                file.write("} // namespace rix\n")