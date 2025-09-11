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
    "string": "std::string",
}


def create_rixmsg_cpp_include(fields: list) -> str:
    includes = set()
    for field in fields:
        if not field["value_type_is_base"]:
            field_type = field["value_type"]
            if "package" in field:
                includes.add(
                    f"#include \"rix/msg/{field['package']}/{field_type}.hpp\""
                )
            else:
                raise ValueError(
                    f"Error: No package specified for type {field['type']}"
                )

    return "\n".join(sorted(includes)) + "\n" if len(includes) > 0 else ""


def create_rixmsg_cpp_fields(fields: list) -> str:
    fields_str = ""
    for field in fields:
        # If we have a base array type
        value_type = field["value_type"]
        key_type = field["key_type"]
        is_static_arr = field["is_static_array"]
        is_dynamic_arr = field["is_dynamic_array"]
        is_map = field["is_map"]
        value_is_base = field["value_type_is_base"]
        key_is_base = field["key_type_is_base"]

        if is_map and not key_is_base:
            raise ValueError(
                f"Error: Value type for associative container cannot be custom type {field['type']}"
            )

        # If we have a base type
        if value_is_base:
            # If we have a dynamic array of base types
            if is_dynamic_arr:
                fields_str += f"std::vector<{CPP_TYPE_BINDINGS[value_type]}> {field['name']}{{}};\n"
            # If we have a static array of base types
            elif is_static_arr:
                arr_size = field["static_array_size"]
                fields_str += f"std::array<{CPP_TYPE_BINDINGS[value_type]}, {arr_size}> {field['name']}{{}};\n"
            # If we have a map type
            elif is_map and key_is_base:
                fields_str += f"std::map<{CPP_TYPE_BINDINGS[key_type]}, {CPP_TYPE_BINDINGS[value_type]}> {field['name']}{{}};\n"
            # If we have a single base type
            else:
                fields_str += (
                    f"{CPP_TYPE_BINDINGS[field['type']]} {field['name']}{{}};\n"
                )
        # If we have a custom type (package specified)
        elif "package" in field:
            # If we have a dynamic array of custom types
            if is_dynamic_arr:
                fields_str += f"std::vector<{field['package']}::{value_type}> {field['name']}{{}};\n"
            # If we have a static array of custom types
            elif is_static_arr:
                arr_size = field["static_array_size"]
                fields_str += f"std::array<{field['package']}::{value_type}, {arr_size}> {field['name']}{{}};\n"
            # If we have a map type
            elif is_map and key_is_base:
                fields_str += f"std::map<{CPP_TYPE_BINDINGS[key_type]}, {field['package']}::{value_type}> {field['name']}{{}};\n"
            # If we have a single custom type
            else:
                fields_str += (
                    f"{field['package']}::{field['type']} {field['name']}{{}};\n"
                )
        # If the package is not specified for the custom type, raise an error
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")

    return fields_str[:-1] if fields_str[-1] == "\n" else fields_str


def create_rixmsg_cpp_size_function(fields: list) -> str:
    size_str = ""
    for field in fields:
        value_type = field["value_type"]
        key_type = field["key_type"]
        is_static_arr = field["is_static_array"]
        is_dynamic_arr = field["is_dynamic_array"]
        is_map = field["is_map"]
        value_is_base = field["value_type_is_base"]
        key_is_base = field["key_type_is_base"]

        if is_map and not key_is_base:
            raise ValueError(
                f"Error: Value type for associative container cannot be custom type {field['type']}"
            )

        # If we have a string
        if value_type == "string":
            if is_dynamic_arr:
                size_str += f"size += size_string_vector({field['name']});\n"
            elif is_static_arr:
                size_str += f"size += size_string_array({field['name']});\n"
            elif is_map:
                if key_type == "string":
                    size_str += f"size += size_string_to_string_map({field['name']});\n"
                else:
                    size_str += f"size += size_number_to_string_map({field['name']});\n"
            else:
                size_str += f"size += size_string({field['name']});\n"
        # If we have a base type other than a string
        elif value_is_base:
            if is_dynamic_arr:
                size_str += f"size += size_number_vector({field['name']});\n"
            # If we have a static array of base types
            elif is_static_arr:
                size_str += f"size += size_number_array({field['name']});\n"
            elif is_map:
                if key_type == "string":
                    size_str += f"size += size_string_to_number_map({field['name']});\n"
                else:
                    size_str += f"size += size_number_to_number_map({field['name']});\n"
            else:
                size_str += f"size += size_number({field['name']});\n"
        # If we have a custom type (package specified)
        elif "package" in field:
            if is_dynamic_arr:
                size_str += f"size += size_message_vector({field['name']});\n"
            elif is_static_arr:
                size_str += f"size += size_message_array({field['name']});\n"
            elif is_map:
                if key_type == "string":
                    size_str += (
                        f"size += size_string_to_message_map({field['name']});\n"
                    )
                else:
                    size_str += (
                        f"size += size_number_to_message_map({field['name']});\n"
                    )
            else:
                size_str += f"size += size_message({field['name']});\n"
        # If the package is not specified for the custom type, raise an error
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")

    return size_str[:-1] if size_str[-1] == "\n" else size_str


def create_rixmsg_cpp_hash(hash: str) -> str:
    return f"{{0x{hash[0:16]}ULL, 0x{hash[16:32]}ULL}}"


def create_rixmsg_cpp_serialize_function(fields: list) -> str:
    serialize_str = ""
    for field in fields:
        value_type = field["value_type"]
        key_type = field["key_type"]
        is_static_arr = field["is_static_array"]
        is_dynamic_arr = field["is_dynamic_array"]
        is_map = field["is_map"]
        value_is_base = field["value_type_is_base"]
        key_is_base = field["key_type_is_base"]

        if is_map and not key_is_base:
            raise ValueError(
                f"Error: Value type for associative container cannot be custom type {field['type']}"
            )

        if value_type == "string":
            if is_dynamic_arr:
                serialize_str += (
                    f"serialize_string_vector(dst, offset, {field['name']});\n"
                )
            elif is_static_arr:
                serialize_str += (
                    f"serialize_string_array(dst, offset, {field['name']});\n"
                )
            elif is_map:
                if key_type == "string":
                    serialize_str += f"serialize_string_to_string_map(dst, offset, {field['name']});\n"
                else:
                    serialize_str += f"serialize_number_to_string_map(dst, offset, {field['name']});\n"
            else:
                serialize_str += f"serialize_string(dst, offset, {field['name']});\n"
        elif value_is_base:
            if is_dynamic_arr:
                serialize_str += (
                    f"serialize_number_vector(dst, offset, {field['name']});\n"
                )
            elif is_static_arr:
                serialize_str += (
                    f"serialize_number_array(dst, offset, {field['name']});\n"
                )
            elif is_map:
                if key_type == "string":
                    serialize_str += f"serialize_string_to_number_map(dst, offset, {field['name']});\n"
                else:
                    serialize_str += f"serialize_number_to_number_map(dst, offset, {field['name']});\n"
            else:
                serialize_str += f"serialize_number(dst, offset, {field['name']});\n"
        elif "package" in field:
            if is_dynamic_arr:
                serialize_str += (
                    f"serialize_message_vector(dst, offset, {field['name']});\n"
                )
            elif is_static_arr:
                serialize_str += (
                    f"serialize_message_array(dst, offset, {field['name']});\n"
                )
            elif is_map:
                if key_type == "string":
                    serialize_str += f"serialize_string_to_message_map(dst, offset, {field['name']});\n"
                else:
                    serialize_str += f"serialize_number_to_message_map(dst, offset, {field['name']});\n"
            else:
                serialize_str += f"serialize_message(dst, offset, {field['name']});\n"
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")

    return serialize_str[:-1] if serialize_str[-1] == "\n" else serialize_str


def create_rixmsg_cpp_deserialize_function(fields: list) -> str:
    deserialize_str = ""
    for field in fields:
        value_type = field["value_type"]
        key_type = field["key_type"]
        is_static_arr = field["is_static_array"]
        is_dynamic_arr = field["is_dynamic_array"]
        is_map = field["is_map"]
        value_is_base = field["value_type_is_base"]
        key_is_base = field["key_type_is_base"]

        if is_map and not key_is_base:
            raise ValueError(
                f"Error: Value type for associative container cannot be custom type {field['type']}"
            )

        if value_type == "string":
            if is_dynamic_arr:
                deserialize_str += f"if (!deserialize_string_vector({field['name']}, src, size, offset)) {{ return false; }};\n"
            elif is_static_arr:
                deserialize_str += f"if (!deserialize_string_array({field['name']}, src, size, offset)) {{ return false; }};\n"
            elif is_map:
                if key_type == "string":
                    deserialize_str += f"if (!deserialize_string_to_string_map({field['name']}, src, size, offset)) {{ return false; }};\n"
                else:
                    deserialize_str += f"if (!deserialize_number_to_string_map({field['name']}, src, size, offset)) {{ return false; }};\n"
            else:
                deserialize_str += f"if (!deserialize_string({field['name']}, src, size, offset)) {{ return false; }};\n"
        elif value_is_base:
            if is_dynamic_arr:
                deserialize_str += f"if (!deserialize_number_vector({field['name']}, src, size, offset)) {{ return false; }};\n"
            elif is_static_arr:
                deserialize_str += f"if (!deserialize_number_array({field['name']}, src, size, offset)) {{ return false; }};\n"
            elif is_map:
                if key_type == "string":
                    deserialize_str += f"if (!deserialize_string_to_number_map({field['name']}, src, size, offset)) {{ return false; }};\n"
                else:
                    deserialize_str += f"if (!deserialize_number_to_number_map({field['name']}, src, size, offset)) {{ return false; }};\n"
            else:
                deserialize_str += f"if (!deserialize_number({field['name']}, src, size, offset)) {{ return false; }};\n"
        elif "package" in field:
            if is_dynamic_arr:
                deserialize_str += f"if (!deserialize_message_vector({field['name']}, src, size, offset)) {{ return false; }};\n"
            elif is_static_arr:
                deserialize_str += f"if (!deserialize_message_array({field['name']}, src, size, offset)) {{ return false; }};\n"
            elif is_map:
                if key_type == "string":
                    deserialize_str += f"if (!deserialize_string_to_message_map({field['name']}, src, size, offset)) {{ return false; }};\n"
                else:
                    deserialize_str += f"if (!deserialize_number_to_message_map({field['name']}, src, size, offset)) {{ return false; }};\n"
            else:
                deserialize_str += f"if (!deserialize_message({field['name']}, src, size, offset)) {{ return false; }};\n"
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")

    return deserialize_str[:-1] if deserialize_str[-1] == "\n" else deserialize_str


def create_rixmsg_cpp(msg: dict) -> str:
    n = "\n"
    return f"""#pragma once

#include <cstdint>
#include <vector>
#include <array>
#include <map>
#include <string>
#include <cstring>

#include "rix/msg/serialization.hpp"
#include "rix/msg/message.hpp"
{create_rixmsg_cpp_include(msg['fields'])}
namespace rix {{
namespace msg {{
namespace {msg['package']} {{

class {msg['name']} : public Message {{
  public:
    {create_rixmsg_cpp_fields(msg['fields']).replace(n, n + '    ')}

    {msg['name']}() = default;
    {msg['name']}(const {msg['name']} &other) = default;
    ~{msg['name']}() = default;

    size_t size() const override {{
        using namespace detail;
        size_t size = 0;
        {create_rixmsg_cpp_size_function(msg['fields']).replace(n, n + '        ')}
        return size;
    }}

    std::array<uint64_t, 2> hash() const override {{
        return {create_rixmsg_cpp_hash(msg['hash'])};
    }}

    void serialize(uint8_t *dst, size_t &offset) const override {{
        using namespace detail;
        {create_rixmsg_cpp_serialize_function(msg['fields']).replace(n, n + '        ')}
    }}

    bool deserialize(const uint8_t *src, size_t size, size_t &offset) override {{
        using namespace detail;
        {create_rixmsg_cpp_deserialize_function(msg['fields']).replace(n, n + '        ')}
        return true;
    }}
}};

}} // namespace {msg['package']}
}} // namespace msg
}} // namespace rix"""
