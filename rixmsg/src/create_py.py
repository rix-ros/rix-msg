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
    "string": '""'
}

def create_rixmsg_py_imports(fields: list) -> str:
    includes = set()
    for field in fields:
        if not field['is_base_type']:
            field_type = field['type_str']
            if 'package' in field:
                includes.add(f"from rixmsg.{field['package']}.{field_type} import {field_type}")
            else:
                raise ValueError(f"Error: No package specified for type {field['type']}")
            
    return "\n".join(sorted(includes)) + "\n" if len(includes) > 0 else ""

def create_rixmsg_py_constructor(fields: list) -> str:
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
                fields_str += f"self.{field['name']} = []\n"
            # If we have a static array of base types
            elif is_static_arr:
                arr_size = field['static_array_size']
                fields_str += f"self.{field['name']} = [{PY_TYPE_INITIALIZERS[field_type_str]} for _ in range({arr_size})]\n"
            # If we have a single base type
            else:
                fields_str += f"self.{field['name']} = {PY_TYPE_INITIALIZERS[field_type_str]}\n"
        # If we have a custom type (package specified)
        elif 'package' in field:
            # If we have a dynamic array of custom types
            if is_dynamic_arr:
                fields_str += f"self.{field['name']} = []\n"
            # If we have a static array of custom types
            elif is_static_arr:
                arr_size = field['static_array_size']
                fields_str += f"self.{field['name']} = [{field_type_str}() for _ in range({arr_size})]\n"
            # If we have a single custom type
            else:
                fields_str += f"self.{field['name']} = {field_type_str}()\n"
        # If the package is not specified for the custom type, raise an error
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")
        
    return fields_str[:-1] if fields_str[-1] == "\n" else fields_str

def create_rixmsg_py_size_function(fields: list) -> str:
    size_str = ""
    for field in fields:
        field_type_str = field['type_str']
        is_dynamic_arr = field['is_dynamic_array']
        is_static_arr = field['is_static_array']
        is_base = field['is_base_type']

        # If we have a string
        if field_type_str == "string":
            if is_dynamic_arr:
                size_str += f"size += MessageBase._size_vector_string(self.{field['name']})\n"
            elif is_static_arr:
                arr_size = field['static_array_size']
                size_str += f"size += MessageBase._size_fixed_array_string(self.{field['name']}, {arr_size})\n"
            else:
                size_str += f"size += MessageBase._size_string(self.{field['name']})\n"
        # If we have a base type other than a string
        elif is_base:
            if is_dynamic_arr:
                size_str += f"size += MessageBase._size_vector_base(self.{field['name']}, MessageBase._size_{field_type_str}())\n"
            # If we have a static array of base types
            elif is_static_arr:
                size_str += f"size += MessageBase._size_fixed_array_base(self.{field['name']}, MessageBase._size_{field_type_str}())\n"
            else:
                size_str += f"size += MessageBase._size_{field_type_str}()\n"
        # If we have a custom type (package specified)
        elif 'package' in field:
            if is_dynamic_arr:
                size_str += f"size += MessageBase._size_vector_custom(self.{field['name']})\n"
            elif is_static_arr:
                arr_size = field['static_array_size']
                size_str += f"size += MessageBase._size_fixed_array_custom(self.{field['name']}, {arr_size})\n"
            else:
                size_str += f"size += MessageBase._size_custom(self.{field['name']})\n"
        # If the package is not specified for the custom type, raise an error
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")
    
    return size_str[:-1] if size_str[-1] == "\n" else size_str

def create_rixmsg_py_hash(hash: str) -> str:
    return f"[0x{hash[0:16]}, 0x{hash[16:32]}]"

def create_rixmsg_py_serialize_function(fields: list) -> str:
    serialize_str = ""
    for field in fields:
        field_type_str = field['type_str']
        is_dynamic_arr = field['is_dynamic_array']
        is_static_arr = field['is_static_array']
        is_base = field['is_base_type']

        if field_type_str == "string":
            if is_dynamic_arr:
                serialize_str += f"MessageBase._serialize_string(self.{field['name']}, buffer, len(self.{field['name']}), False)\n"
            elif is_static_arr:
                arr_size = field['static_array_size']
                serialize_str += f"MessageBase._serialize_string(self.{field['name']}, buffer, {arr_size}, True)\n"
            else:
                serialize_str += f"MessageBase._serialize_string(self.{field['name']}, buffer)\n"
        elif is_base:
            if is_dynamic_arr:
                serialize_str += f"MessageBase._serialize_{field_type_str}(self.{field['name']}, buffer, len(self.{field['name']}), False)\n"
            elif is_static_arr:
                arr_size = field['static_array_size']
                serialize_str += f"MessageBase._serialize_{field_type_str}(self.{field['name']}, buffer, {arr_size}, True)\n"
            else:
                serialize_str += f"MessageBase._serialize_{field_type_str}(self.{field['name']}, buffer)\n"
        elif 'package' in field:
            if is_dynamic_arr:
                serialize_str += f"MessageBase._serialize_custom(self.{field['name']}, buffer, len(self.{field['name']}), False)\n"
            elif is_static_arr:
                arr_size = field['static_array_size']
                serialize_str += f"MessageBase._serialize_custom(self.{field['name']}, buffer, {arr_size}, True)\n"
            else:
                serialize_str += f"MessageBase._serialize_custom(self.{field['name']}, buffer)\n"
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")
    
    return serialize_str[:-1] if serialize_str[-1] == "\n" else serialize_str
            
def create_rixmsg_py_deserialize_function(fields: list) -> str:
    deserialize_str = ""
    for field in fields:
        field_type_str = field['type_str']
        is_dynamic_arr = field['is_dynamic_array']
        is_static_arr = field['is_static_array']
        is_base = field['is_base_type']

        if field_type_str == "string":
            if is_dynamic_arr:
                deserialize_str += f"self.{field['name']} = MessageBase._deserialize_string(buffer, context, False)\n"
            elif is_static_arr:
                arr_size = field['static_array_size']
                deserialize_str += f"self.{field['name']} = MessageBase._deserialize_string(buffer, context, True, {arr_size})\n"
            else:
                deserialize_str += f"self.{field['name']} = MessageBase._deserialize_string(buffer, context)\n"
        elif is_base:
            if is_dynamic_arr:
                deserialize_str += f"self.{field['name']} = MessageBase._deserialize_{field_type_str}(buffer, context, False)\n"
            elif is_static_arr:
                arr_size = field['static_array_size']
                deserialize_str += f"self.{field['name']} = MessageBase._deserialize_{field_type_str}(buffer, context, True, {arr_size})\n"
            else:
                deserialize_str += f"self.{field['name']} = MessageBase._deserialize_{field_type_str}(buffer, context)\n"
        elif 'package' in field:
            if is_dynamic_arr:
                deserialize_str += f"self.{field['name']} = MessageBase._deserialize_custom(buffer, context, {field_type_str}, False)\n"
            elif is_static_arr:
                arr_size = field['static_array_size']
                deserialize_str += f"self.{field['name']} = MessageBase._deserialize_custom(buffer, context, {field_type_str}, True, {arr_size})\n"
            else:
                deserialize_str += f"self.{field['name']} = MessageBase._deserialize_custom(buffer, context, {field_type_str})\n"
        else:
            raise ValueError(f"Error: No package specified for type {field['type']}")
        
    return deserialize_str[:-1] if deserialize_str[-1] == "\n" else deserialize_str

# def create_rixmsg_py_from_pb(fields: list) -> str:
#     from_pb_str = ""
#     for field in fields:
#         if field['is_base_type']:
#             from_pb_str += f"self.{field['name']} = pbuff.{field['name']}\n"
#         else:
#             from_pb_str += f"self.{field['name']}.from_pb(pbuff.{field['name']})\n"
#     return from_pb_str[:-1] if from_pb_str[-1] == "\n" else from_pb_str

# def create_rixmsg_py_to_pb(fields: list) -> str:
#     to_pb_str = ""
#     for field in fields:
#         to_pb_str += f"pbuff.{field['name']} = self.{field['name']}\n"
#     return to_pb_str[:-1] if to_pb_str[-1] == "\n" else to_pb_str

# def create_rixmsg_py(msg: dict) -> str:
#     return f"""from rixmsg.message_base import MessageBase
# import rixmsg.protobuf.{msg['package']}.{msg['name']}_pb2 as pb
# {create_rixmsg_py_imports(msg['fields'])}
# class {msg['name']}(MessageBase):
#     def __init__(self):
#         {create_rixmsg_py_constructor(msg['fields']).replace('\n', '\n        ')}

#     def size(self) -> int:
#         size = 0
#         {create_rixmsg_py_size_function(msg['fields']).replace('\n', '\n        ')}
#         return size
    
#     def serialize(self, buffer: bytearray) -> None:
#         {create_rixmsg_py_serialize_function(msg['fields']).replace('\n', '\n        ')}

#     def deserialize(self, buffer: bytearray, context: dict) -> None:
#         {create_rixmsg_py_deserialize_function(msg['fields']).replace('\n', '\n        ')}

#     def hash(self) -> int:
#         return {create_rixmsg_py_hash(msg['hash'])}

#     def from_pb(self, pbuff) -> None:
#         {create_rixmsg_py_from_pb(msg['fields']).replace('\n', '\n        ')}

#     def to_pb(self) -> None:
#         pbuff = pb.{msg['name']}()
#         {create_rixmsg_py_to_pb(msg['fields']).replace('\n', '\n        ')}
#         return pbuff"""

def create_rixmsg_py(msg: dict) -> str:
    n = '\n'
    return f"""from rixmsg.message_base import MessageBase
{create_rixmsg_py_imports(msg['fields'])}
class {msg['name']}(MessageBase):
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