from message import Message
from field import Field

PY_TYPE_INITIALIZERS = {
    "char": "'\\0'",
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
}

PY_TYPE_HINTS = {
    "char": "str",
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
}


def create_rixmsg_py_imports(fields: list[Field]) -> str:
    includes: set[str] = set()
    for field in fields:
        if not field.value_is_base:
            field_type = field.value_type
            if field.package is not None:
                includes.add(
                    f"from rixmsg.{field.package}.{field_type} import {field_type}"
                )
            else:
                raise ValueError(
                    f"Error: No package specified for type {field.type_str}"
                )

    return "\n".join(sorted(includes)) + "\n" if len(includes) > 0 else ""


def create_rixmsg_py_constructor(fields: list[Field]) -> str:
    fields_str = ""
    for field in fields:
        # If we have a base type
        if field.value_is_base:
            # If we have a dynamic array of base types
            if field.is_dynamic_array:
                fields_str += f"self.{field.name}: list[{PY_TYPE_HINTS[field.value_type]}] = []\n"
            # If we have a static array of base types
            elif field.is_static_array:
                arr_size = field.static_array_size
                fields_str += f"self.{field.name}: list[{PY_TYPE_HINTS[field.value_type]}] = [{PY_TYPE_INITIALIZERS[field.value_type]} for _ in range({arr_size})]\n"
            # If we have a map
            elif field.is_map:
                fields_str += f"self.{field.name}: dict[{PY_TYPE_HINTS[field.key_type]}, {PY_TYPE_HINTS[field.value_type]}] = {{}}\n"
            # If we have a single base type
            else:
                fields_str += (
                    f"self.{field.name}: {PY_TYPE_HINTS[field.value_type]} = {PY_TYPE_INITIALIZERS[field.value_type]}\n"
                )
        # If we have a message type (package specified)
        elif field.package is not None:
            # If we have a dynamic array of message types
            if field.is_dynamic_array:
                fields_str += f"self.{field.name}: list[\"{field.value_type}\"] = []\n"
            # If we have a static array of message types
            elif field.is_static_array:
                arr_size = field.static_array_size
                fields_str += f"self.{field.name}: list[\"{field.value_type}\"] = [{field.value_type}() for _ in range({arr_size})]\n"
            elif field.is_map:
                fields_str += f"self.{field.name}: dict[{PY_TYPE_HINTS[field.key_type]}, \"{field.value_type}\"] = {{}}\n"
            # If we have a single message type
            else:
                fields_str += f"self.{field.name}: \"{field.value_type}\" = {field.value_type}()\n"
        # If the package is not specified for the message type, raise an error
        else:
            raise ValueError(f"Error: No package specified for type {field.type_str}")

    return fields_str[:-1] if len(fields_str) > 0 else fields_str


def create_rixmsg_py_size_function(fields: list[Field]) -> str:
    size_str = ""
    for field in fields:
        # If we have a string
        if field.value_type == "string":
            if field.is_dynamic_array:
                size_str += f"size += Message._size_vector_string(self.{field.name})\n"
            elif field.is_static_array:
                arr_size = field.static_array_size
                size_str += f"size += Message._size_array_string(self.{field.name}, {arr_size})\n"
            elif field.is_map:
                if field.key_type == "string":
                    size_str += f"size += Message._size_map_string_to_string(self.{field.name})\n"
                else:
                    size_str += f"size += Message._size_map_number_to_string(self.{field.name}, Message._size_{field.key_type}())\n"
            else:
                size_str += f"size += Message._size_string(self.{field.name})\n"
        # If we have a base type other than a string
        elif field.value_is_base:
            if field.is_dynamic_array:
                size_str += f"size += Message._size_vector_number(self.{field.name}, Message._size_{field.value_type}())\n"
            # If we have a static array of base types
            elif field.is_static_array:
                size_str += f"size += Message._size_array_number(self.{field.name}, Message._size_{field.value_type}())\n"
            elif field.is_map:
                if field.key_type == "string":
                    size_str += f"size += Message._size_map_string_to_number(self.{field.name}, Message._size_{field.value_type}())\n"
                else:
                    size_str += f"size += Message._size_map_number_to_number(self.{field.name}, Message._size_{field.key_type}(), Message._size_{field.value_type}())\n"
            else:
                size_str += f"size += Message._size_{field.value_type}()\n"
        # If we have a message type (package specified)
        elif field.package is not None:
            if field.is_dynamic_array:
                size_str += f"size += Message._size_vector_message(self.{field.name})\n"
            elif field.is_static_array:
                arr_size = field.static_array_size
                size_str += f"size += Message._size_array_message(self.{field.name}, {arr_size})\n"
            elif field.is_map:
                if field.key_type == "string":
                    size_str += f"size += Message._size_map_string_to_message(self.{field.name})\n"
                else:
                    size_str += f"size += Message._size_map_number_to_message(self.{field.name}, Message._size_{field.key_type}())\n"
            else:
                size_str += f"size += Message._size_message(self.{field.name})\n"
        # If the package is not specified for the message type, raise an error
        else:
            raise ValueError(f"Error: No package specified for type {field.type_str}")

    return size_str[:-1] if len(size_str) > 0 else size_str


def create_rixmsg_py_hash(hash: str) -> str:
    return f"[0x{hash[0:16]}, 0x{hash[16:32]}]"


def create_rixmsg_py_serialize_function(fields: list[Field]) -> str:
    serialize_str = ""
    for field in fields:
        if field.value_type == "string":
            if field.is_dynamic_array:
                serialize_str += (
                    f"Message._serialize_string_vector(self.{field.name}, buffer)\n"
                )
            elif field.is_static_array:
                serialize_str += f"Message._serialize_string_array(self.{field.name}, buffer, {field.static_array_size})\n"
            elif field.is_map:
                if field.key_type == "string":
                    serialize_str += f"Message._serialize_map(self.{field.name}, buffer, Message._serialize_string_vector, Message._serialize_string_vector)\n"
                else:
                    serialize_str += f"Message._serialize_map(self.{field.name}, buffer, Message._serialize_{field.key_type}_vector, Message._serialize_string_vector)\n"
            else:
                serialize_str += (
                    f"Message._serialize_string(self.{field.name}, buffer)\n"
                )
        elif field.value_is_base:
            if field.is_dynamic_array:
                serialize_str += f"Message._serialize_{field.value_type}_vector(self.{field.name}, buffer)\n"
            elif field.is_static_array:
                serialize_str += f"Message._serialize_{field.value_type}_array(self.{field.name}, buffer, {field.static_array_size})\n"
            elif field.is_map:
                if field.key_type == "string":
                    serialize_str += f"Message._serialize_map(self.{field.name}, buffer, Message._serialize_string_vector, Message._serialize_{field.value_type}_vector)\n"
                else:
                    serialize_str += f"Message._serialize_map(self.{field.name}, buffer, Message._serialize_{field.key_type}_vector, Message._serialize_{field.value_type}_vector)\n"
            else:
                serialize_str += f"Message._serialize_{field.value_type}(self.{field.name}, buffer)\n"
        elif field.package is not None:
            if field.is_dynamic_array:
                serialize_str += (
                    f"Message._serialize_message_vector(self.{field.name}, buffer)\n"
                )
            elif field.is_static_array:
                serialize_str += f"Message._serialize_message_array(self.{field.name}, buffer, {field.static_array_size})\n"
            elif field.is_map:
                if field.key_type == "string":
                    serialize_str += f"Message._serialize_map(self.{field.name}, buffer, Message._serialize_string_vector, Message._serialize_message_vector)\n"
                else:
                    serialize_str += f"Message._serialize_map(self.{field.name}, buffer, Message._serialize_{field.key_type}_vector, Message._serialize_message_vector)\n"
            else:
                serialize_str += (
                    f"Message._serialize_message(self.{field.name}, buffer)\n"
                )
        else:
            raise ValueError(f"Error: No package specified for type {field.type_str}")

    return serialize_str[:-1] if len(serialize_str) > 0 else serialize_str


def create_rixmsg_py_deserialize_function(fields: list[Field]) -> str:
    deserialize_str = ""
    for field in fields:
        if field.value_type == "string":
            if field.is_dynamic_array:
                deserialize_str += f"self.{field.name} = Message._deserialize_string_vector(buffer, offset)\n"
            elif field.is_static_array:
                deserialize_str += f"self.{field.name} = Message._deserialize_string_array(buffer, offset, {field.static_array_size})\n"
            elif field.is_map:
                if field.key_type == "string":
                    deserialize_str += f"self.{field.name} = Message._deserialize_map(buffer, offset, Message._deserialize_string_vector, Message._deserialize_string_vector)\n"
                else:
                    deserialize_str += f"self.{field.name} = Message._deserialize_map(buffer, offset, Message._deserialize_{field.key_type}_vector, Message._deserialize_string_vector)\n"
            else:
                deserialize_str += (
                    f"self.{field.name} = Message._deserialize_string(buffer, offset)\n"
                )
        elif field.value_is_base:
            if field.is_dynamic_array:
                deserialize_str += f"self.{field.name} = Message._deserialize_{field.value_type}_vector(buffer, offset)\n"
            elif field.is_static_array:
                arr_size = field.static_array_size
                deserialize_str += f"self.{field.name} = Message._deserialize_{field.value_type}_array(buffer, offset, {arr_size})\n"
            elif field.is_map:
                if field.key_type == "string":
                    deserialize_str += f"self.{field.name} = Message._deserialize_map(buffer, offset, Message._deserialize_string_vector, Message._deserialize_{field.value_type}_vector)\n"
                else:
                    deserialize_str += f"self.{field.name} = Message._deserialize_map(buffer, offset, Message._deserialize_{field.key_type}_vector, Message._deserialize_{field.value_type}_vector)\n"
            else:
                deserialize_str += f"self.{field.name} = Message._deserialize_{field.value_type}(buffer, offset)\n"
        elif field.package is not None:
            if field.is_dynamic_array:
                deserialize_str += f"self.{field.name} = Message._deserialize_message_vector(buffer, offset, {field.value_type})\n"
            elif field.is_static_array:
                arr_size = field.static_array_size
                deserialize_str += f"self.{field.name} = Message._deserialize_message_array(buffer, offset, {arr_size}, {field.value_type})\n"
            elif field.is_map:
                if field.key_type == "string":
                    deserialize_str += f"self.{field.name} = Message._deserialize_map(buffer, offset, Message._deserialize_string_vector, Message._deserialize_message_vector, {field.value_type})\n"
                else:
                    deserialize_str += f"self.{field.name} = Message._deserialize_map(buffer, offset, Message._deserialize_{field.key_type}_vector, Message._deserialize_message_vector, {field.value_type})\n"
            else:
                deserialize_str += f"self.{field.name} = Message._deserialize_message(buffer, offset, {field.value_type})\n"
        else:
            raise ValueError(f"Error: No package specified for type {field.type_str}")

    return deserialize_str[:-1] if len(deserialize_str) > 0 else deserialize_str


def create_rixmsg_py(msg: Message) -> str:
    n = "\n"
    return f"""from rixmsg.message import Message
{create_rixmsg_py_imports(msg.fields)}
class {msg.name}(Message):
    def __init__(self):
        {create_rixmsg_py_constructor(msg.fields).replace(n, n + '        ')}

    def size(self) -> int:
        size = 0
        {create_rixmsg_py_size_function(msg.fields).replace(n, n + '        ')}
        return size
    
    def serialize(self, buffer: bytearray) -> None:
        {create_rixmsg_py_serialize_function(msg.fields).replace(n, n + '        ')}

    def deserialize(self, buffer: bytearray, offset: Message.Offset) -> None:
        {create_rixmsg_py_deserialize_function(msg.fields).replace(n, n + '        ')}

    def hash(self) -> list[int]:
        return {create_rixmsg_py_hash(msg.hash)}"""
