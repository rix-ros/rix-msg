from message import Message
from field import Field

JS_TYPE_INITIALIZERS = {
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
    "bool": "false",
    "string": "''",
}


def create_rixmsg_js_imports(fields: list[Field]) -> str:
    includes: set[str] = set()
    for field in fields:
        if not field.value_is_base:
            field_type = field.value_type
            if field.package is not None:
                includes.add(
                    f'import {{ {field_type} }} from "../{field.package}/{field_type}.js";'
                )
            else:
                raise ValueError(
                    f"Error: No package specified for type {field.type_str}"
                )

    return "\n".join(sorted(includes)) + "\n" if len(includes) > 0 else ""


def create_rixmsg_js_constructor(fields: list[Field]) -> str:
    fields_str = ""
    for field in fields:
        # If we have a base type
        if field.value_is_base:
            # If we have a dynamic array of base types
            if field.is_dynamic_array:
                fields_str += f"this.{field.name} = [];\n"
            # If we have a static array of base types
            elif field.is_static_array:
                arr_size = field.static_array_size
                fields_str += f"this.{field.name} = Array.from({{length: {arr_size}}}, () => {JS_TYPE_INITIALIZERS[field.value_type]});\n"
            # If we have a map:
            elif field.is_map:
                fields_str += f"this.{field.name} = {{}};"
            # If we have a single base type
            else:
                fields_str += (
                    f"this.{field.name} = {JS_TYPE_INITIALIZERS[field.value_type]};\n"
                )
        # If we have a message type (package specified)
        elif field.package is not None:
            # If we have a dynamic array of message types
            if field.is_dynamic_array:
                fields_str += f"this.{field.name} = [];\n"
            # If we have a static array of message types
            elif field.is_static_array:
                arr_size = field.static_array_size
                fields_str += f"this.{field.name} = Array.from({{length: {arr_size}}}, () => new {field.value_type}());\n"
            # If we have a map:
            elif field.is_map:
                fields_str += f"this.{field.name} = {{}};"
            # If we have a single message type
            else:
                fields_str += f"this.{field.name} = new {field.value_type}();\n"
        # If the package is not specified for the message type, raise an error
        else:
            raise ValueError(f"Error: No package specified for type {field.type_str}")

    return fields_str[:-1] if len(fields_str) > 0 else fields_str


def create_rixmsg_js_size_function(fields: list[Field]) -> str:
    size_str = ""
    for field in fields:
        # If we have a string
        if field.value_type == "string":
            if field.is_dynamic_array:
                size_str += f"size += Message._size_vector_string(this.{field.name});\n"
            elif field.is_static_array:
                arr_size = field.static_array_size
                size_str += f"size += Message._size_array_string(this.{field.name}, {arr_size});\n"
            elif field.is_map:
                if field.key_type == "string":
                    size_str += f"size += Message._size_map_string_to_string(this.{field.name})\n"
                else:
                    size_str += f"size += Message._size_map_number_to_string(this.{field.name}, Message._size_{field.key_type}())\n"
            else:
                size_str += f"size += Message._size_string(this.{field.name});\n"
        # If we have a base type other than a string
        elif field.value_is_base:
            if field.is_dynamic_array:
                size_str += f"size += Message._size_vector_number(this.{field.name}, Message._size_{field.value_type}());\n"
            # If we have a static array of base types
            elif field.is_static_array:
                arr_size = field.static_array_size
                size_str += f"size += Message._size_array_number(this.{field.name}, Message._size_{field.value_type}());\n"
            elif field.is_map:
                if field.key_type == "string":
                    size_str += f"size += Message._size_map_string_to_number(this.{field.name}, Message._size_{field.value_type}())\n"
                else:
                    size_str += f"size += Message._size_map_number_to_number(this.{field.name}, Message._size_{field.key_type}(), Message._size_{field.value_type}())\n"
            else:
                size_str += f"size += Message._size_{field.value_type}();\n"
        # If we have a message type (package specified)
        elif field.package is not None:
            if field.is_dynamic_array:
                size_str += (
                    f"size += Message._size_vector_message(this.{field.name});\n"
                )
            elif field.is_static_array:
                arr_size = field.static_array_size
                size_str += f"size += Message._size_array_message(this.{field.name}, {arr_size});\n"
            elif field.is_map:
                if field.key_type == "string":
                    size_str += f"size += Message._size_map_string_to_message(this.{field.name})\n"
                else:
                    size_str += f"size += Message._size_map_number_to_message(this.{field.name}, Message._size_{field.key_type}())\n"
            else:
                size_str += f"size += Message._size_message(this.{field.name});\n"
        # If the package is not specified for the message type, raise an error
        else:
            raise ValueError(f"Error: No package specified for type {field.type_str}")

    return size_str[:-1] if len(size_str) > 0 else size_str


def create_rixmsg_js_hash(hash: str) -> str:
    return f"[BigInt(0x{hash[0:16]}), BigInt(0x{hash[16:32]})]"


def create_rixmsg_js_serialize_function(fields: list[Field]) -> str:
    serialize_str = ""
    for field in fields:
        if field.value_type == "string":
            if field.is_dynamic_array:
                serialize_str += f"buffer = Message._serialize_vector(this.{field.name}, buffer, Message._serialize_string);\n"
            elif field.is_static_array:
                arr_size = field.static_array_size
                serialize_str += f"buffer = Message._serialize_array(this.{field.name}, buffer, Message._serialize_string, {arr_size});\n"
            elif field.is_map:
                if field.key_type == "string":
                    serialize_str += f"buffer = Message._serialize_map(this.{field.name}, buffer, Message._serialize_string, Message._serialize_string)\n"
                else:
                    serialize_str += f"buffer = Message._serialize_map(this.{field.name}, buffer, Message._serialize_{field.key_type}, Message._serialize_string)\n"
            else:
                serialize_str += (
                    f"buffer = Message._serialize_string(this.{field.name}, buffer);\n"
                )
        elif field.value_is_base:
            if field.is_dynamic_array:
                serialize_str += f"buffer = Message._serialize_vector(this.{field.name}, buffer, Message._serialize_{field.value_type});\n"
            elif field.is_static_array:
                arr_size = field.static_array_size
                serialize_str += f"buffer = Message._serialize_array(this.{field.name}, buffer, Message._serialize_{field.value_type}, {arr_size});\n"
            elif field.is_map:
                if field.key_type == "string":
                    serialize_str += f"buffer = Message._serialize_map(this.{field.name}, buffer, Message._serialize_string, Message._serialize_{field.value_type})\n"
                else:
                    serialize_str += f"buffer = Message._serialize_map(this.{field.name}, buffer, Message._serialize_{field.key_type}, Message._serialize_{field.value_type})\n"
            else:
                serialize_str += f"buffer = Message._serialize_{field.value_type}(this.{field.name}, buffer);\n"
        elif field.package is not None:
            if field.is_dynamic_array:
                serialize_str += f"buffer = Message._serialize_vector(this.{field.name}, buffer, Message._serialize_message);\n"
            elif field.is_static_array:
                arr_size = field.static_array_size
                serialize_str += f"buffer = Message._serialize_array(this.{field.name}, buffer, Message._serialize_message, {arr_size});\n"
            elif field.is_map:
                if field.key_type == "string":
                    serialize_str += f"buffer = Message._serialize_map(this.{field.name}, buffer, Message._serialize_string, Message._serialize_message)\n"
                else:
                    serialize_str += f"buffer = Message._serialize_map(this.{field.name}, buffer, Message._serialize_{field.key_type}, Message._serialize_message)\n"
            else:
                serialize_str += (
                    f"buffer = Message._serialize_message(this.{field.name}, buffer);\n"
                )
        else:
            raise ValueError(f"Error: No package specified for type {field.type_str}")

    return serialize_str[:-1] if len(serialize_str) > 0 else serialize_str


def create_rixmsg_js_deserialize_function(fields: list[Field]) -> str:
    deserialize_str = ""
    for field in fields:
        if field.value_type == "string":
            if field.is_dynamic_array:
                deserialize_str += f"this.{field.name} = Message._deserialize_vector(buffer, context, Message._deserialize_string);\n"
            elif field.is_static_array:
                arr_size = field.static_array_size
                deserialize_str += f"this.{field.name} = Message._deserialize_array(buffer, context, Message._deserialize_string, {arr_size});\n"
            elif field.is_map:
                if field.key_type == "string":
                    deserialize_str += f"this.{field.name} = Message._deserialize_map(buffer, context, Message._deserialize_string, Message._deserialize_string)\n"
                else:
                    deserialize_str += f"this.{field.name} = Message._deserialize_map(buffer, context, Message._deserialize_{field.key_type}, Message._deserialize_string)\n"
            else:
                deserialize_str += f"this.{field.name} = Message._deserialize_string(buffer, context);\n"
        elif field.value_is_base:
            if field.is_dynamic_array:
                deserialize_str += f"this.{field.name} = Message._deserialize_vector(buffer, context, Message._deserialize_{field.value_type});\n"
            elif field.is_static_array:
                arr_size = field.static_array_size
                deserialize_str += f"this.{field.name} = Message._deserialize_array(buffer, context, Message._deserialize_{field.value_type}, {arr_size});\n"
            elif field.is_map:
                if field.key_type == "string":
                    deserialize_str += f"this.{field.name} = Message._deserialize_map(buffer, context, Message._deserialize_string, Message._deserialize_{field.value_type})\n"
                else:
                    deserialize_str += f"this.{field.name} = Message._deserialize_map(buffer, context, Message._deserialize_{field.key_type}, Message._deserialize_{field.value_type})\n"
            else:
                deserialize_str += f"this.{field.name} = Message._deserialize_{field.value_type}(buffer, context);\n"
        elif field.package is not None:
            if field.is_dynamic_array:
                deserialize_str += f"this.{field.name} = Message._deserialize_vector(buffer, context, Message._deserialize_message, {field.value_type});\n"
            elif field.is_static_array:
                arr_size = field.static_array_size
                deserialize_str += f"this.{field.name} = Message._deserialize_array(buffer, context, Message._deserialize_message, {arr_size}, {field.value_type});\n"
            elif field.is_map:
                if field.key_type == "string":
                    deserialize_str += f"this.{field.name} = Message._deserialize_map(buffer, context, Message._deserialize_string, Message._deserialize_message, {field.value_type})\n"
                else:
                    deserialize_str += f"this.{field.name} = Message._deserialize_map(buffer, context, Message._deserialize_{field.key_type}, Message._deserialize_message, {field.value_type})\n"
            else:
                deserialize_str += f"this.{field.name} = Message._deserialize_message(buffer, context, {field.value_type});\n"
        else:
            raise ValueError(f"Error: No package specified for type {field.type_str}")

    return deserialize_str[:-1] if len(deserialize_str) > 0 else deserialize_str


def create_rixmsg_js(msg: Message) -> str:
    n = "\n"
    return f"""import {{ Message }} from "../message.js";
{create_rixmsg_js_imports(msg.fields)}
export class {msg.name} extends Message {{
    constructor() {{
        super();
        {create_rixmsg_js_constructor(msg.fields).replace(n, n + '        ')}
    }}

    size() {{
        let size = 0;
        {create_rixmsg_js_size_function(msg.fields).replace(n, n + '        ')}
        return size;
    }}

    hash() {{
        return {create_rixmsg_js_hash(msg.hash).replace(n, n + '        ')};
    }}

    serialize(buffer) {{
        {create_rixmsg_js_serialize_function(msg.fields).replace(n, n + '        ')}
        return buffer;
    }}

    deserialize(buffer, context) {{
        {create_rixmsg_js_deserialize_function(msg.fields).replace(n, n + '        ')}
    }}
}}"""
