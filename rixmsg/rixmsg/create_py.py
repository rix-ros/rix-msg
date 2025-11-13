from message import Message
from field import Field
from typing import List

PY_TYPE_INITIALIZERS = {
    "char": "b'\\0'",
    "int8": "0",
    "int16": "0",
    "int32": "0",
    "int64": "0",
    "uint8": "0",
    "uint16": "0",
    "uint32": "0",
    "uint64": "0",
    "float": "0.0",
    "double": "0.0",
    "bool": "False",
    "string": '""',
    "pointer": "memoryview(bytearray())",
}

PY_TYPE_HINTS = {
    "char": "bytes",
    "int8": "int",
    "int16": "int",
    "int32": "int",
    "int64": "int",
    "uint8": "int",
    "uint16": "int",
    "uint32": "int",
    "uint64": "int",
    "float": "float",
    "double": "float",
    "bool": "bool",
    "string": "str",
    "pointer": "memoryview",
}


def get_init_functions(fields: List[Field]) -> str:
    init_str = ""
    for field in fields:
        if field.value_is_base:
            init_str += f"init_{field.value_type}"
            if field.is_dynamic_array:
                init_str += f"_vector(self, '{field.name}')\n"
            elif field.is_static_array:
                init_str += f"_array(self, '{field.name}', {field.static_array_size})\n"
            else:
                init_str += f"(self, '{field.name}')\n"
        else:
            init_str += f"init_message"
            if field.is_dynamic_array:
                init_str += f"_vector(self, '{field.name}', {field.value_type})\n"
            elif field.is_static_array:
                init_str += f"_array(self, '{field.name}', {field.value_type}, {field.static_array_size})\n"
            else:
                init_str += f"(self, '{field.name}', {field.value_type})\n"

    return init_str


def get_property_names(fields: list[Field]) -> str:
    if len(fields) == 0:
        return "self._property_names = []\n"

    property_names = "self._property_names = ["
    for field in fields:
        property_names += f"'{field.name}', "
    property_names = property_names[:-2] + "]\n"
    return property_names


def get_member_initializers(fields: list[Field]) -> str:
    init_str = ""
    for field in fields:
        if field.is_dynamic_array:
            init_str += f"self.{field.name} = []\n"
        elif field.value_is_base and field.is_static_array:
            init_str += f"self.{field.name} = [{PY_TYPE_INITIALIZERS[field.value_type]} for _ in range({field.static_array_size})]\n"
        elif field.value_is_base:
            init_str += (
                f"self.{field.name} = {PY_TYPE_INITIALIZERS[field.value_type]}\n"
            )
        elif not field.value_is_base and field.is_static_array:
            init_str += f"self.{field.name} = [{field.value_type}() for _ in range({field.static_array_size})]\n"
        else:
            init_str += f"self.{field.name} = {field.value_type}()\n"
    return init_str[:-1] if len(init_str) > 0 else init_str


def create_rixmsg_py_imports(fields: list[Field]) -> str:
    includes: set[str] = set()
    for field in fields:
        if not field.value_is_base:
            field_type = field.value_type
            if field.package is not None:
                includes.add(
                    f"from rix.{field.package}.{field_type} import {field_type}"
                )
            else:
                raise ValueError(
                    f"Error: No package specified for type {field.type_str}"
                )

    return "\n".join(sorted(includes)) + "\n" if len(includes) > 0 else ""


def create_rixmsg_py_constructor(fields: list[Field]) -> str:
    fields_str = ""
    fields_str += get_init_functions(fields)
    fields_str += get_property_names(fields)
    fields_str += get_member_initializers(fields)
    return fields_str


def create_rixmsg_py_hash(hash: str) -> str:
    return f"[0x{hash[0:16]}, 0x{hash[16:32]}]"


def create_rixmsg_py_resize(fields: list[Field]) -> str:
    resize_str = ""
    for field in fields:
        is_dynamic = (
            field.is_dynamic_array
            or (field.value_type == "string")
            or (field.value_type == "pointer")
            or not field.value_is_base
        )
        if is_dynamic:
            resize_str += f"resize(self, '{field.name}', buffer, offset)\n"
    return resize_str[:-1] if len(resize_str) > 0 else resize_str


def create_rixmsg_py_get_prefix_len(fields: list[Field]) -> str:
    get_prefix_len_str = ""
    for field in fields:
        is_dynamic = (
            field.is_dynamic_array
            or (field.value_type == "string")
            or (field.value_type == "pointer")
            or not field.value_is_base
        )
        if is_dynamic:
            get_prefix_len_str += (
                f"prefix_len += get_prefix_len(self, '{field.name}')\n"
            )
    return (
        get_prefix_len_str[:-1] if len(get_prefix_len_str) > 0 else get_prefix_len_str
    )


def create_rixmsg_py_get_prefix(fields: list[Field]) -> str:
    get_prefix_str = ""
    for field in fields:
        is_dynamic = (
            field.is_dynamic_array
            or (field.value_type == "string")
            or (field.value_type == "pointer")
            or not field.value_is_base
        )
        if is_dynamic:
            get_prefix_str += f"get_prefix(self, '{field.name}', buffer, offset)\n"
    if len(get_prefix_str) == 0:
        return "pass"
    return get_prefix_str[:-1] if len(get_prefix_str) > 0 else get_prefix_str


def create_rixmsg_py_get_segment_count(fields: list[Field]) -> str:
    segment_count_str = ""

    # Each non-dynamic field adds one segment. A dynamic field here is a vector of strings, a vector of custom types, or a custom type.
    segment_count = 0
    dynamic_fields: list[Field] = []
    for field in fields:
        is_dynamic = (
            (field.is_dynamic_array and field.value_type == "string")
            or (field.is_static_array and field.value_type == "string")
            or (field.is_dynamic_array and field.value_type == "pointer")
            or (field.is_static_array and field.value_type == "pointer")
            or (field.is_dynamic_array and not field.value_is_base)
            or (not field.value_is_base)
        )
        if is_dynamic:
            dynamic_fields.append(field)
        else:
            segment_count += 1
    if segment_count > 0:
        segment_count_str += f"count += {segment_count}\n"
    for field in dynamic_fields:
        segment_count_str += f"count += get_segment_count(self, '{field.name}')\n"

    return segment_count_str[:-1] if len(segment_count_str) > 0 else segment_count_str


def create_rixmsg_py(msg: Message) -> str:
    n = "\n"
    return f"""from rix.msg import *
{create_rixmsg_py_imports(msg.fields)}
class {msg.name}(Message):
    def __init__(self):
        {create_rixmsg_py_constructor(msg.fields).replace(n, n + '        ')}

    def hash(self) -> list[int]:
        return {create_rixmsg_py_hash(msg.hash)}

    def resize(self, buffer: bytes, length: int, offset: Serializable.Offset) -> bool:
        if length < offset.value + self.get_prefix_len():
            return False
        {create_rixmsg_py_resize(msg.fields).replace(n, n + '        ')}
        return True
    
    def get_prefix_len(self) -> int:
        prefix_len = 0
        {create_rixmsg_py_get_prefix_len(msg.fields).replace(n, n + '        ')}
        return prefix_len

    def get_prefix(self, buffer: bytearray, offset: Message.Offset) -> None:
        {create_rixmsg_py_get_prefix(msg.fields).replace(n, n + '        ')}

    def get_segment_count(self) -> int:
        count = 0
        {create_rixmsg_py_get_segment_count(msg.fields).replace(n, n + '        ')}
        return count

    def get_segments(self) -> list[memoryview]:
        segments = []
        for prop_name in self._property_names:
            prop_descriptor = type(self).__dict__[prop_name]
            segments.extend(prop_descriptor.get_segments(self))
        return segments
"""
