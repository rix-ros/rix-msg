PROTOBUF_TYPE_BINDINGS = {
    'int8': 'int32',
    'int16': 'int32',
    'int32': 'int32',
    'int64': 'int64',
    'uint8': 'uint32',
    'uint16': 'uint32',
    'uint32': 'uint32',
    'uint64': 'uint64',
    'float': 'float',
    'double': 'double',
    'bool': 'bool',
    'string': 'string',
    'char': 'string'
}

def create_rixmsg_protobuf_imports(fields: list) -> str:
    includes = set()
    for field in fields:
        if not field['is_base_type']:
            field_type = field['type_str']
            if 'package' in field:
                includes.add(f"import \"rixmsg/protobuf/{field['package']}/{field_type}.proto\";")
            else:
                raise ValueError(f"Error: No package specified for type {field['type']}")
            
    return "\n".join(sorted(includes)) + "\n" if len(includes) > 0 else ""

def create_rixmsg_protobuf_fields(fields: list) -> str:
    fields_str = ""
    field_number = 1
    for field in fields:
        # If we have a base array type
        field_type_str = field['type_str']
        is_dynamic_arr = field['is_dynamic_array']
        is_static_arr = field['is_static_array']
        is_base = field['is_base_type']

        if is_base:
            # If we have a dynamic array of base types
            if is_dynamic_arr or is_static_arr:
                fields_str += f"repeated {PROTOBUF_TYPE_BINDINGS[field_type_str]} {field['name']} = {field_number};\n"
            # If we have a single base type
            else:
                fields_str += f"optional {PROTOBUF_TYPE_BINDINGS[field_type_str]} {field['name']} = {field_number};\n"
        else:
            # If we have a dynamic array of non-base types
            if is_dynamic_arr or is_static_arr:
                fields_str += f"repeated {field_type_str} {field['name']} = {field_number};\n"
            # If we have a single non-base type
            else:
                fields_str += f"optional {field_type_str} {field['name']} = {field_number};\n"

        field_number += 1
        
    return fields_str[:-1] if fields_str[-1] == "\n" else fields_str

def create_rixmsg_protobuf(msg: dict) -> str:
    return f"""syntax="proto3";
package rixmsg.protobuf.{msg['package']};
{create_rixmsg_protobuf_imports(msg['fields'])}
message {msg['name']} {{
  {create_rixmsg_protobuf_fields(msg['fields']).replace('\n', '\n  ')}
}}"""