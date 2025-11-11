from message import Message
from field import Field

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
    "pointer": "ptr_t"
}


def create_rixmsg_cpp_include(fields: list[Field]) -> str:
    includes: set[str] = set()
    for field in fields:
        if not field.value_is_base:
            if field.package is not None:
                includes.add(
                    f'#include "rix/{field.package}/{field.value_type}.hpp"'
                )
            else:
                raise ValueError(
                    f"Error: No package specified for type {field.value_type}"
                )

    return "\n".join(sorted(includes)) + "\n" if len(includes) > 0 else ""


def create_rixmsg_cpp_fields(fields: list[Field]) -> str:
    fields_str = ""
    for field in fields:
        # If we have a base type
        if field.value_is_base:
            # If we have a dynamic array of base types
            if field.is_dynamic_array:
                fields_str += f"std::vector<{CPP_TYPE_BINDINGS[field.value_type]}> {field.name}{{}};\n"
            # If we have a static array of base types
            elif field.is_static_array:
                fields_str += f"std::array<{CPP_TYPE_BINDINGS[field.value_type]}, {field.static_array_size}> {field.name}{{}};\n"
            # If we have a single base type
            else:
                fields_str += f"{CPP_TYPE_BINDINGS[field.type_str]} {field.name}{{}};\n"
        # If we have a custom type (package specified)
        elif field.package is not None:
            # If we have a dynamic array of custom types
            if field.is_dynamic_array:
                fields_str += f"std::vector<{field.package}::{field.value_type}> {field.name}{{}};\n"
            # If we have a static array of custom types
            elif field.is_static_array:
                arr_size = field.static_array_size
                fields_str += f"std::array<{field.package}::{field.value_type}, {arr_size}> {field.name}{{}};\n"
            # If we have a single custom type
            else:
                fields_str += f"{field.package}::{field.value_type} {field.name}{{}};\n"
        # If the package is not specified for the custom type, raise an error
        else:
            raise ValueError(f"Error: No package specified for type {field.type_str}")

    return fields_str[:-1] if len(fields_str) > 0 else fields_str


def create_rixmsg_cpp_hash(hash: str) -> str:
    return f"{{0x{hash[0:16]}ULL, 0x{hash[16:32]}ULL}}"


def create_rixmsg_cpp_equal_to(fields: list[Field]) -> str:
    equal_str = ""
    for field in fields:
        equal_str += f"if (this->{field.name} != other.{field.name}) {{ return false; }}\n"
    equal_str += "return true;"
    return equal_str


def create_rixmsg_cpp_segment_count(fields: list[Field]) -> str:
    segment_count_str = ""

    # Each non-dynamic field adds one segment. A dynamic field here is a vector of strings, array of strings, a vector of custom types, or a custom type.
    segment_count = 0
    dynamic_fields: list[Field] = []
    for field in fields:
        is_dynamic = (
            (field.is_dynamic_array and field.value_type == "string") or
            (field.is_static_array and field.value_type == "string") or
            (field.is_dynamic_array and field.value_type == "pointer") or
            (field.is_static_array and field.value_type == "pointer") or
            (field.is_dynamic_array and not field.value_is_base) or
            (not field.value_is_base)
        )
        if is_dynamic:
            dynamic_fields.append(field)
        else:
            segment_count += 1

    segment_count_str += f"count += {segment_count};\n"
    for field in dynamic_fields:
        segment_count_str += f"count += detail::get_segment_count(this->{field.name});\n"

    return segment_count_str[:-1] if len(segment_count_str) > 0 else segment_count_str


def create_rixmsg_cpp_get_segments(fields: list[Field]) -> str:
    get_segments_str = ""
    for field in fields:
        get_segments_str += f"detail::get_segments(this->{field.name}, segments, offset);\n"
    return get_segments_str[:-1] if len(get_segments_str) > 0 else get_segments_str


def create_rixmsg_cpp_get_prefix_len(fields: list[Field]) -> str:
    get_prefix_len_str = ""
    for field in fields:
        is_dynamic = (
            field.is_dynamic_array
            or (field.value_type == "string")
            or (field.value_type == "pointer")
            or not field.value_is_base
        )
        if is_dynamic:
            get_prefix_len_str += f"len += detail::get_prefix_len(this->{field.name});\n"
    return (
        get_prefix_len_str[:-1] if len(get_prefix_len_str) > 0 else get_prefix_len_str
    )


def create_rixmsg_cpp_get_prefix(fields: list[Field]) -> str:
    get_prefix_str = ""
    for field in fields:
        is_dynamic = (
            field.is_dynamic_array
            or (field.value_type == "string")
            or (field.value_type == "pointer")
            or not field.value_is_base
        )
        if is_dynamic:
            get_prefix_str += f"detail::get_prefix(this->{field.name}, dst, offset);\n"
    return get_prefix_str[:-1] if len(get_prefix_str) > 0 else get_prefix_str


def create_rixmsg_cpp_resize(fields: list[Field]) -> str:
    resize_str = ""
    for field in fields:
        is_dynamic = (
            field.is_dynamic_array
            or (field.value_type == "string")
            or (field.value_type == "pointer")
            or not field.value_is_base
        )
        if is_dynamic:
            resize_str += f"detail::resize(this->{field.name}, src, offset);\n"
    return resize_str[:-1] if len(resize_str) > 0 else resize_str


def create_rixmsg_cpp(msg: Message) -> str:
    n = "\n"
    return f"""#pragma once

#include <cstdint>
#include <vector>
#include <array>
#include <string>
#include <cstring>

#include "rix/msg/message.hpp"
#include "rix/msg/serialization.hpp"
{create_rixmsg_cpp_include(msg.fields)}
namespace rix {{
namespace {msg.package} {{

class {msg.name} : public Message {{
  public:
    using Message::get_prefix;
    using Message::get_segments;

    {create_rixmsg_cpp_fields(msg.fields).replace(n, n + '    ')}

    {msg.name}() = default;
    {msg.name}(const {msg.name} &other) = default;
    ~{msg.name}() = default;

    std::array<uint64_t, 2> hash() const override {{
        return {create_rixmsg_cpp_hash(msg.hash)};
    }}

    bool operator==(const {msg.name} &other) const {{
        {create_rixmsg_cpp_equal_to(msg.fields).replace(n, n + '        ')}
    }}

    bool operator!=(const {msg.name} &other) const {{
        return !(*this == other);
    }}

    size_t get_segment_count() const override {{
        size_t count = 0;
        {create_rixmsg_cpp_segment_count(msg.fields).replace(n, n + '        ')}
        return count;
    }}

    bool get_segments(MessageSegment *segments, size_t len, size_t &offset) override {{
        if (len < offset + get_segment_count()) {{
            return false;
        }}
        {create_rixmsg_cpp_get_segments(msg.fields).replace(n, n + '        ')}
        return true;
    }}

    bool get_segments(ConstMessageSegment *segments, size_t len, size_t &offset) const override {{
        if (len < offset + get_segment_count()) {{
            return false;
        }}
        {create_rixmsg_cpp_get_segments(msg.fields).replace(n, n + '        ')}
        return true;
    }}

    uint32_t get_prefix_len() const override {{
        uint32_t len = 0;
        {create_rixmsg_cpp_get_prefix_len(msg.fields).replace(n, n + '        ')}
        return len;
    }}

    void get_prefix(uint8_t *dst, size_t &offset) const override {{
        {create_rixmsg_cpp_get_prefix(msg.fields).replace(n, n + '        ')}
    }}

    bool resize(const uint8_t *src, size_t len, size_t &offset) override {{
        if (len < offset + get_prefix_len()) {{
            return false;
        }}
        {create_rixmsg_cpp_resize(msg.fields).replace(n, n + '        ')}
        return true;
    }}
}};

}} // namespace {msg.package}
}} // namespace rix"""
