from type_regex import is_static_array, is_dynamic_array, is_base_type, get_static_array_size, get_type

CPP_TYPE_BINDINGS = {
    "char": "char",
    "int8": "int8_t",
    "int16": "int16_t",
    "int32": "int32_t",
    "int64": "int64_t",
    "uint8": "uint8_t",
    "uint16": "uint16_t",
    "uint32": "uint32_t",
    "uint64": "uint64_t",
    "float": "float",
    "double": "double",
    "bool": "bool",
    "string": "std::string"
}

def create_rixmsg_cpp_include(fields: list) -> str:
    includes = set()
    for field in fields:
        if not field['is_base_type']:
            field_type = field['type_str']
            if 'package' in field:
                includes.add(f"#include \"rix/msg/{field['package']}/{field_type}.hpp\"")
            else:
                raise ValueError(f"Error: No package specified for type {field['type']}")
            
    return "\n".join(sorted(includes)) + "\n" if len(includes) > 0 else ""

def create_rixmsg_cpp_fields(fields: list) -> str:
    fields_str = ""
    for field in fields:
        # If we have a base array type
        field_type_str = field['type_str']
        is_dynamic_arr = field['is_dynamic_array']
        is_static_arr = field['is_static_array']
        is_base = field['is_base_type']

        # If we have a base type
        if is_base:
            # If we have a dynamic array of base types
            if is_dynamic_arr:
                fields_str += f"std::vector<{CPP_TYPE_BINDINGS[field_type_str]}> {field['name']};\n"
            # If we have a static array of base types
            elif is_static_arr:
                arr_size = field['static_array_size']
                fields_str += f"std::array<{CPP_TYPE_BINDINGS[field_type_str]}, {arr_size}> {field['name']};\n"
            # If we have a single base type
            else:
                fields_str += f"{CPP_TYPE_BINDINGS[field['type']]} {field['name']};\n"
        # If we have a custom type (package specified)
        elif 'package' in field:
            # If we have a dynamic array of custom types
            if is_dynamic_arr:
                fields_str += f"std::vector<{field['package']}::{field_type_str}> {field['name']};\n"
            # If we have a static array of custom types
            elif is_static_arr:
                arr_size = field['static_array_size']
                fields_str += f"std::array<{field['package']}::{field_type_str}, {arr_size}> {field['name']};\n"
            # If we have a single custom type
            else:
                fields_str += f"{field['package']}::{field['type']} {field['name']};\n"
        # If the package is not specified for the custom type, raise an error
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")
        
    return fields_str[:-1] if fields_str[-1] == "\n" else fields_str

def create_rixmsg_cpp_size_function(fields: list) -> str:
    size_str = ""
    for field in fields:
        field_type_str = field['type_str']
        is_dynamic_arr = field['is_dynamic_array']
        is_static_arr = field['is_static_array']
        is_base = field['is_base_type']

        # If we have a string
        if field_type_str == "string":
            if is_dynamic_arr:
                size_str += f"size += size_string_vec({field['name']});\n"
            elif is_static_arr:
                size_str += f"size += size_string_arr({field['name']});\n"
            else:
                size_str += f"size += size_string({field['name']});\n"
        # If we have a base type other than a string
        elif is_base:
            if is_dynamic_arr:
                size_str += f"size += size_base_vec({field['name']});\n"
            # If we have a static array of base types
            elif is_static_arr:
                size_str += f"size += size_base_arr({field['name']});\n"
            else:
                size_str += f"size += size_base({field['name']});\n"
        # If we have a custom type (package specified)
        elif 'package' in field:
            if is_dynamic_arr:
                size_str += f"size += size_custom_vec({field['name']});\n"
            elif is_static_arr:
                size_str += f"size += size_custom_arr({field['name']});\n"
            else:
                size_str += f"size += size_custom({field['name']});\n"
        # If the package is not specified for the custom type, raise an error
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")
    
    return size_str[:-1] if size_str[-1] == "\n" else size_str

def create_rixmsg_cpp_hash(hash: str) -> str:
    return f"{{0x{hash[0:16]}ULL, 0x{hash[16:32]}ULL}}"

def create_rixmsg_cpp_serialize_function(fields: list) -> str:
    serialize_str = ""
    for field in fields:
        field_type_str = field['type_str']
        is_dynamic_arr = field['is_dynamic_array']
        is_static_arr = field['is_static_array']
        is_base = field['is_base_type']

        if field_type_str == "string":
            if is_dynamic_arr:
                serialize_str += f"serialize_string_vec({field['name']}, buffer);\n"
            elif is_static_arr:
                serialize_str += f"serialize_string_arr({field['name']}, buffer);\n"
            else:
                serialize_str += f"serialize_string({field['name']}, buffer);\n"
        elif is_base:
            if is_dynamic_arr:
                serialize_str += f"serialize_base_vec({field['name']}, buffer);\n"
            elif is_static_arr:
                serialize_str += f"serialize_base_arr({field['name']}, buffer);\n"
            else:
                serialize_str += f"serialize_base({field['name']}, buffer);\n"
        elif 'package' in field:
            if is_dynamic_arr:
                serialize_str += f"serialize_custom_vec({field['name']}, buffer);\n"
            elif is_static_arr:
                serialize_str += f"serialize_custom_arr({field['name']}, buffer);\n"
            else:
                serialize_str += f"serialize_custom({field['name']}, buffer);\n"
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")
    
    return serialize_str[:-1] if serialize_str[-1] == "\n" else serialize_str
            
def create_rixmsg_cpp_deserialize_function(fields: list) -> str:
    deserialize_str = ""
    for field in fields:
        field_type_str = field['type_str']
        is_dynamic_arr = field['is_dynamic_array']
        is_static_arr = field['is_static_array']
        is_base = field['is_base_type']

        if field_type_str == "string":
            if is_dynamic_arr:
                deserialize_str += f"deserialize_string_vec({field['name']}, buffer, offset);\n"
            elif is_static_arr:
                deserialize_str += f"deserialize_string_arr({field['name']}, buffer, offset);\n"
            else:
                deserialize_str += f"deserialize_string({field['name']}, buffer, offset);\n"
        elif is_base:
            if is_dynamic_arr:
                deserialize_str += f"deserialize_base_vec({field['name']}, buffer, offset);\n"
            elif is_static_arr:
                deserialize_str += f"deserialize_base_arr({field['name']}, buffer, offset);\n"
            else:
                deserialize_str += f"deserialize_base({field['name']}, buffer, offset);\n"
        elif 'package' in field:
            if is_dynamic_arr:
                deserialize_str += f"deserialize_custom_vec({field['name']}, buffer, offset);\n"
            elif is_static_arr:
                deserialize_str += f"deserialize_custom_arr({field['name']}, buffer, offset);\n"
            else:
                deserialize_str += f"deserialize_custom({field['name']}, buffer, offset);\n"
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")
        
    return deserialize_str[:-1] if deserialize_str[-1] == "\n" else deserialize_str

def add_flags_to_fields(fields: list) -> None:
    for field in fields:
        field_type = field['type']
        field['is_static_array'] = is_static_array(field_type)
        field['is_dynamic_array'] = is_dynamic_array(field_type)
        field['is_base_type'] = is_base_type(field_type)
        field['static_array_size'] = get_static_array_size(field_type)
        field['type_str'] = get_type(field_type)

def create_rixmsg_cpp(msg: dict) -> str:
    # Precalculate type flags for each field
    add_flags_to_fields(msg['fields'])

    return f"""#pragma once

#include <cstdint>
#include <vector>
#include <string>
#include <cstring>

#include "rix/msg/message_base.hpp"
#include "rix/msg/serializer.hpp"
{create_rixmsg_cpp_include(msg['fields'])}
namespace rix {{
namespace msg {{
namespace {msg['package']} {{

class {msg['name']} : public MessageBase {{
  public:
    {create_rixmsg_cpp_fields(msg['fields']).replace('\n', '\n    ')}

    {msg['name']}() = default;
    {msg['name']}(const {msg['name']} &other) = default;
    ~{msg['name']}() = default;

  private:
    size_t size() const override {{
        size_t size = 0;
        {create_rixmsg_cpp_size_function(msg['fields']).replace('\n', '\n        ')}
        return size;
    }}

    rix::msg::Hash hash() const override {{
        return {create_rixmsg_cpp_hash(msg['hash'])};
    }}

    void serialize(std::vector<uint8_t> &buffer) const override {{
        buffer.reserve(buffer.size() + this->size());
        {create_rixmsg_cpp_serialize_function(msg['fields']).replace('\n', '\n        ')}
    }}

    void deserialize(const std::vector<uint8_t> &buffer, size_t &offset) override {{
        {create_rixmsg_cpp_deserialize_function(msg['fields']).replace('\n', '\n        ')}
    }}
}};

}} // namespace {msg['package']}
}} // namespace msg
}} // namespace rix"""