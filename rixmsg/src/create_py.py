PY_TYPE_INITIALIZERS = {
    "char": "''",
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


def create_rixmsg_py_imports(fields: list) -> str:
    includes = set()
    for field in fields:
        if not field["value_type_is_base"]:
            field_type = field["value_type"]
            if "package" in field:
                includes.add(
                    f"from rixmsg.{field['package']}.{field_type} import {field_type}"
                )
            else:
                raise ValueError(
                    f"Error: No package specified for type {field['type']}"
                )

    return "\n".join(sorted(includes)) + "\n" if len(includes) > 0 else ""


def create_rixmsg_py_constructor(fields: list) -> str:
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
                fields_str += f"self.{field['name']} = []\n"
            # If we have a static array of base types
            elif is_static_arr:
                arr_size = field["static_array_size"]
                fields_str += f"self.{field['name']} = [{PY_TYPE_INITIALIZERS[value_type]} for _ in range({arr_size})]\n"
            # If we have a map
            elif is_map:
                fields_str += f"self.{field['name']} = {{}}\n"
            # If we have a single base type
            else:
                fields_str += (
                    f"self.{field['name']} = {PY_TYPE_INITIALIZERS[value_type]}\n"
                )
        # If we have a message type (package specified)
        elif "package" in field:
            # If we have a dynamic array of message types
            if is_dynamic_arr:
                fields_str += f"self.{field['name']} = []\n"
            # If we have a static array of message types
            elif is_static_arr:
                arr_size = field["static_array_size"]
                fields_str += f"self.{field['name']} = [{value_type}() for _ in range({arr_size})]\n"
            elif is_map:
                fields_str += f"self.{field['name']} = {{}}\n"
            # If we have a single message type
            else:
                fields_str += f"self.{field['name']} = {value_type}()\n"
        # If the package is not specified for the message type, raise an error
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")

    return fields_str[:-1] if fields_str[-1] == "\n" else fields_str


def create_rixmsg_py_size_function(fields: list) -> str:
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
                size_str += (
                    f"size += Message._size_vector_string(self.{field['name']})\n"
                )
            elif is_static_arr:
                arr_size = field["static_array_size"]
                size_str += f"size += Message._size_array_string(self.{field['name']}, {arr_size})\n"
            elif is_map:
                if key_type == "string":
                    size_str += f"size += Message._size_map_string_to_string(self.{field['name']})\n"
                else:
                    size_str += f"size += Message._size_map_number_to_string(self.{field['name']}, Message._size_{key_type}())\n"
            else:
                size_str += f"size += Message._size_string(self.{field['name']})\n"
        # If we have a base type other than a string
        elif value_is_base:
            if is_dynamic_arr:
                size_str += f"size += Message._size_vector_number(self.{field['name']}, Message._size_{value_type}())\n"
            # If we have a static array of base types
            elif is_static_arr:
                size_str += f"size += Message._size_array_number(self.{field['name']}, Message._size_{value_type}())\n"
            elif is_map:
                if key_type == "string":
                    size_str += f"size += Message._size_map_string_to_number(self.{field['name']}, Message._size_{value_type}())\n"
                else:
                    size_str += f"size += Message._size_map_number_to_number(self.{field['name']}, Message._size_{key_type}(), Message._size_{value_type}())\n"
            else:
                size_str += f"size += Message._size_{value_type}()\n"
        # If we have a message type (package specified)
        elif "package" in field:
            if is_dynamic_arr:
                size_str += (
                    f"size += Message._size_vector_message(self.{field['name']})\n"
                )
            elif is_static_arr:
                arr_size = field["static_array_size"]
                size_str += f"size += Message._size_array_message(self.{field['name']}, {arr_size})\n"
            elif is_map:
                if key_type == "string":
                    size_str += f"size += Message._size_map_string_to_message(self.{field['name']})\n"
                else:
                    size_str += f"size += Message._size_map_number_to_message(self.{field['name']}, Message._size_{key_type}())\n"
            else:
                size_str += f"size += Message._size_message(self.{field['name']})\n"
        # If the package is not specified for the message type, raise an error
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")

    return size_str[:-1] if size_str[-1] == "\n" else size_str


def create_rixmsg_py_hash(hash: str) -> str:
    return f"[0x{hash[0:16]}, 0x{hash[16:32]}]"


def create_rixmsg_py_serialize_function(fields: list) -> str:
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
                serialize_str += f"Message._serialize_string(self.{field['name']}, buffer, len(self.{field['name']}), False)\n"
            elif is_static_arr:
                arr_size = field["static_array_size"]
                serialize_str += f"Message._serialize_string(self.{field['name']}, buffer, {arr_size}, True)\n"
            elif is_map:
                if key_type == "string":
                    serialize_str += f"Message._serialize_map(self.{field['name']}, buffer, Message._serialize_string, Message._serialize_string)\n"
                else:
                    serialize_str += f"Message._serialize_map(self.{field['name']}, buffer, Message._serialize_{key_type}, Message._serialize_string)\n"
            else:
                serialize_str += (
                    f"Message._serialize_string(self.{field['name']}, buffer)\n"
                )
        elif value_is_base:
            if is_dynamic_arr:
                serialize_str += f"Message._serialize_{value_type}(self.{field['name']}, buffer, len(self.{field['name']}), False)\n"
            elif is_static_arr:
                arr_size = field["static_array_size"]
                serialize_str += f"Message._serialize_{value_type}(self.{field['name']}, buffer, {arr_size}, True)\n"
            elif is_map:
                if key_type == "string":
                    serialize_str += f"Message._serialize_map(self.{field['name']}, buffer, Message._serialize_string, Message._serialize_{value_type})\n"
                else:
                    serialize_str += f"Message._serialize_map(self.{field['name']}, buffer, Message._serialize_{key_type}, Message._serialize_{value_type})\n"
            else:
                serialize_str += (
                    f"Message._serialize_{value_type}(self.{field['name']}, buffer)\n"
                )
        elif "package" in field:
            if is_dynamic_arr:
                serialize_str += f"Message._serialize_message(self.{field['name']}, buffer, len(self.{field['name']}), False)\n"
            elif is_static_arr:
                arr_size = field["static_array_size"]
                serialize_str += f"Message._serialize_message(self.{field['name']}, buffer, {arr_size}, True)\n"
            elif is_map:
                if key_type == "string":
                    serialize_str += f"Message._serialize_map(self.{field['name']}, buffer, Message._serialize_string, Message._serialize_message)\n"
                else:
                    serialize_str += f"Message._serialize_map(self.{field['name']}, buffer, Message._serialize_{key_type}, Message._serialize_message)\n"
            else:
                serialize_str += (
                    f"Message._serialize_message(self.{field['name']}, buffer)\n"
                )
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")

    return serialize_str[:-1] if serialize_str[-1] == "\n" else serialize_str


def create_rixmsg_py_deserialize_function(fields: list) -> str:
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
                deserialize_str += f"self.{field['name']} = Message._deserialize_string(buffer, context, False)\n"
            elif is_static_arr:
                arr_size = field["static_array_size"]
                deserialize_str += f"self.{field['name']} = Message._deserialize_string(buffer, context, True, {arr_size})\n"
            elif is_map:
                if key_type == "string":
                    deserialize_str += f"self.{field['name']} = Message._deserialize_map(buffer, context, Message._deserialize_string, Message._deserialize_string)\n"
                else:
                    deserialize_str += f"self.{field['name']} = Message._deserialize_map(buffer, context, Message._deserialize_{key_type}, Message._deserialize_string)\n"
            else:
                deserialize_str += f"self.{field['name']} = Message._deserialize_string(buffer, context)\n"
        elif value_is_base:
            if is_dynamic_arr:
                deserialize_str += f"self.{field['name']} = Message._deserialize_{value_type}(buffer, context, False)\n"
            elif is_static_arr:
                arr_size = field["static_array_size"]
                deserialize_str += f"self.{field['name']} = Message._deserialize_{value_type}(buffer, context, True, {arr_size})\n"
            elif is_map:
                if key_type == "string":
                    deserialize_str += f"self.{field['name']} = Message._deserialize_map(buffer, context, Message._deserialize_string, Message._deserialize_{value_type})\n"
                else:
                    deserialize_str += f"self.{field['name']} = Message._deserialize_map(buffer, context, Message._deserialize_{key_type}, Message._deserialize_{value_type})\n"
            else:
                deserialize_str += f"self.{field['name']} = Message._deserialize_{value_type}(buffer, context)\n"
        elif "package" in field:
            if is_dynamic_arr:
                deserialize_str += f"self.{field['name']} = Message._deserialize_message(buffer, context, {value_type}, False)\n"
            elif is_static_arr:
                arr_size = field["static_array_size"]
                deserialize_str += f"self.{field['name']} = Message._deserialize_message(buffer, context, {value_type}, True, {arr_size})\n"
            elif is_map:
                if key_type == "string":
                    deserialize_str += f"self.{field['name']} = Message._deserialize_map(buffer, context, Message._deserialize_string, Message._deserialize_message, {value_type})\n"
                else:
                    deserialize_str += f"self.{field['name']} = Message._deserialize_map(buffer, context, Message._deserialize_{key_type}, Message._deserialize_message, {value_type})\n"
            else:
                deserialize_str += f"self.{field['name']} = Message._deserialize_message(buffer, context, {value_type})\n"
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")

    return deserialize_str[:-1] if deserialize_str[-1] == "\n" else deserialize_str

def create_rixmsg_py(msg: dict) -> str:
    n = "\n"
    return f"""from rixmsg.message import Message
{create_rixmsg_py_imports(msg['fields'])}
class {msg['name']}(Message):
    def __init__(self):
        {create_rixmsg_py_constructor(msg['fields']).replace(n, n + '        ')}

    def size(self) -> int:
        size = 0
        {create_rixmsg_py_size_function(msg['fields']).replace(n, n + '        ')}
        return size
    
    def serialize(self, buffer: bytearray) -> None:
        {create_rixmsg_py_serialize_function(msg['fields']).replace(n, n + '        ')}

    def deserialize(self, buffer: bytearray, context: dict) -> None:
        {create_rixmsg_py_deserialize_function(msg['fields']).replace(n, n + '        ')}

    def hash(self) -> int:
        return {create_rixmsg_py_hash(msg['hash'])}"""
