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
    "string": "''"
}

def create_rixmsg_js_imports(fields: list) -> str:
    includes = set()
    for field in fields:
        if not field['is_base_type']:
            field_type = field['type_str']
            if 'package' in field:
                includes.add(f"import {{ {field_type} }} from \"../{field['package']}/{field_type}.js\";")
            else:
                raise ValueError(f"Error: No package specified for type {field['type']}")
            
    return "\n".join(sorted(includes)) + "\n" if len(includes) > 0 else ""

def create_rixmsg_js_constructor(fields: list) -> str:
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
                fields_str += f"this.{field['name']} = [];\n"
            # If we have a static array of base types
            elif is_static_arr:
                arr_size = field['static_array_size']
                fields_str += f"this.{field['name']} = Array.from({{length: {arr_size}}}, () => {JS_TYPE_INITIALIZERS[field_type_str]});\n"
            # If we have a single base type
            else:
                fields_str += f"this.{field['name']} = {JS_TYPE_INITIALIZERS[field_type_str]};\n"
        # If we have a custom type (package specified)
        elif 'package' in field:
            # If we have a dynamic array of custom types
            if is_dynamic_arr:
                fields_str += f"this.{field['name']} = [];\n"
            # If we have a static array of custom types
            elif is_static_arr:
                arr_size = field['static_array_size']
                fields_str += f"this.{field['name']} = Array.from({{length: {arr_size}}}, () => new {field_type_str}());\n"
            # If we have a single custom type
            else:
                fields_str += f"this.{field['name']} = new {field_type_str}();\n"
        # If the package is not specified for the custom type, raise an error
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")
        
    return fields_str[:-1] if fields_str[-1] == "\n" else fields_str

def create_rixmsg_js_size_function(fields: list) -> str:
    size_str = ""
    for field in fields:
        field_type_str = field['type_str']
        is_dynamic_arr = field['is_dynamic_array']
        is_static_arr = field['is_static_array']
        is_base = field['is_base_type']

        # If we have a string
        if field_type_str == "string":
            if is_dynamic_arr:
                size_str += f"size += MessageBase._size_vector_string(this.{field['name']});\n"
            elif is_static_arr:
                arr_size = field['static_array_size']
                size_str += f"size += MessageBase._size_fixed_array_string(this.{field['name']}, {arr_size});\n"
            else:
                size_str += f"size += MessageBase._size_string(this.{field['name']});\n"
        # If we have a base type other than a string
        elif is_base:
            if is_dynamic_arr:
                size_str += f"size += MessageBase._size_vector_base(this.{field['name']}, MessageBase._size_{field_type_str}());\n"
            # If we have a static array of base types
            elif is_static_arr:
                arr_size = field['static_array_size']
                size_str += f"size += MessageBase._size_fixed_array_base(this.{field['name']}, MessageBase._size_{field_type_str}());\n"
            else:
                size_str += f"size += MessageBase._size_{field_type_str}();\n"
        # If we have a custom type (package specified)
        elif 'package' in field:
            if is_dynamic_arr:
                size_str += f"size += MessageBase._size_vector_custom(this.{field['name']});\n"
            elif is_static_arr:
                arr_size = field['static_array_size']
                size_str += f"size += MessageBase._size_fixed_array_custom(this.{field['name']}, {arr_size});\n"
            else:
                size_str += f"size += MessageBase._size_custom(this.{field['name']});\n"
        # If the package is not specified for the custom type, raise an error
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")
    
    return size_str[:-1] if size_str[-1] == "\n" else size_str

def create_rixmsg_js_hash(hash: str) -> str:
    return f"[BigInt(0x{hash[0:16]}), BigInt(0x{hash[16:32]})]"

def create_rixmsg_js_serialize_function(fields: list) -> str:
    serialize_str = ""
    for field in fields:
        field_type_str = field['type_str']
        is_dynamic_arr = field['is_dynamic_array']
        is_static_arr = field['is_static_array']
        is_base = field['is_base_type']

        if field_type_str == "string":
            if is_dynamic_arr:
                serialize_str += f"buffer = MessageBase._serialize_vector(this.{field['name']}, buffer, MessageBase._serialize_string);\n"
            elif is_static_arr:
                arr_size = field['static_array_size']
                serialize_str += f"buffer = MessageBase._serialize_fixed_array(this.{field['name']}, buffer, MessageBase._serialize_string, {arr_size});\n"
            else:
                serialize_str += f"buffer = MessageBase._serialize_string(this.{field['name']}, buffer);\n"
        elif is_base:
            if is_dynamic_arr:
                serialize_str += f"buffer = MessageBase._serialize_vector(this.{field['name']}, buffer, MessageBase._serialize_{field_type_str});\n"
            elif is_static_arr:
                arr_size = field['static_array_size']
                serialize_str += f"buffer = MessageBase._serialize_fixed_array(this.{field['name']}, buffer, MessageBase._serialize_{field_type_str}, {arr_size});\n"
            else:
                serialize_str += f"buffer = MessageBase._serialize_{field_type_str}(this.{field['name']}, buffer);\n"
        elif 'package' in field:
            if is_dynamic_arr:
                serialize_str += f"buffer = MessageBase._serialize_vector(this.{field['name']}, buffer, MessageBase._serialize_custom);\n"
            elif is_static_arr:
                arr_size = field['static_array_size']
                serialize_str += f"buffer = MessageBase._serialize_fixed_array(this.{field['name']}, buffer, MessageBase._serialize_custom, {arr_size});\n"
            else:
                serialize_str += f"buffer = MessageBase._serialize_custom(this.{field['name']}, buffer);\n"
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")
    
    return serialize_str[:-1] if serialize_str[-1] == "\n" else serialize_str
            
def create_rixmsg_js_deserialize_function(fields: list) -> str:
    deserialize_str = ""
    for field in fields:
        field_type_str = field['type_str']
        is_dynamic_arr = field['is_dynamic_array']
        is_static_arr = field['is_static_array']
        is_base = field['is_base_type']

        if field_type_str == "string":
            if is_dynamic_arr:
                deserialize_str += f"this.{field['name']} = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_string);\n"
            elif is_static_arr:
                arr_size = field['static_array_size']
                deserialize_str += f"this.{field['name']} = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_string, {arr_size});\n"
            else:
                deserialize_str += f"this.{field['name']} = MessageBase._deserialize_string(buffer, context);\n"
        elif is_base:
            if is_dynamic_arr:
                deserialize_str += f"this.{field['name']} = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_{field_type_str});\n"
            elif is_static_arr:
                arr_size = field['static_array_size']
                deserialize_str += f"this.{field['name']} = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_{field_type_str}, {arr_size});\n"
            else:
                deserialize_str += f"this.{field['name']} = MessageBase._deserialize_{field_type_str}(buffer, context);\n"
        elif 'package' in field:
            if is_dynamic_arr:
                deserialize_str += f"this.{field['name']} = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_custom, {field_type_str});\n"
            elif is_static_arr:
                arr_size = field['static_array_size']
                deserialize_str += f"this.{field['name']} = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_custom, {arr_size}, {field_type_str});\n"
            else:
                deserialize_str += f"this.{field['name']} = MessageBase._deserialize_custom(buffer, context, {field_type_str});\n"
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")
        
    return deserialize_str[:-1] if deserialize_str[-1] == "\n" else deserialize_str

def create_rixmsg_js(msg: dict) -> str:
    return f"""import {{ MessageBase }} from "../message_base.js";
{create_rixmsg_js_imports(msg['fields'])}
export class {msg['name']} extends MessageBase {{
    constructor() {{
        super();
        {create_rixmsg_js_constructor(msg['fields']).replace('\n', '\n        ')}
    }}

    size() {{
        let size = 0;
        {create_rixmsg_js_size_function(msg['fields']).replace('\n', '\n        ')}
        return size;
    }}

    hash() {{
        return {create_rixmsg_js_hash(msg['hash']).replace('\n', '\n        ')};
    }}

    serialize(buffer) {{
        {create_rixmsg_js_serialize_function(msg['fields']).replace('\n', '\n        ')}
        return buffer;
    }}

    deserialize(buffer, context) {{
        {create_rixmsg_js_deserialize_function(msg['fields']).replace('\n', '\n        ')}
    }}
}}"""