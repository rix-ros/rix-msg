import re
from base_types import BaseTypes

def is_valid(input_text):
    pattern = re.compile(r"^(?:[a-zA-Z_][a-zA-Z0-9_]*\[[0-9]*\]|[a-zA-Z_][a-zA-Z0-9_]*|[a-zA-Z_][a-zA-Z0-9_]+)$")
    return pattern.match(input_text) is not None

def get_type(input_text):
    pattern = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)(?:\[[0-9]*\])?$")
    match = pattern.search(input_text)
    if match:
        return match.group(1)
    return None
        
def is_array(input_text):
    # return is_static_array(input_text) or is_dynamic_array(input_text)
    pattern = re.compile(r"^[A-Za-z0-9]+\[[0-9]*\]$")
    return pattern.match(input_text) is not None

def is_static_array(input_text):
    pattern = re.compile(r"^[A-Za-z0-9]+\[[0-9]+\]$")
    return pattern.match(input_text) is not None

def get_static_array_size(input_text):
    pattern = re.compile(r"\[([0-9]+)\]$")
    match = pattern.search(input_text)
    if match:
        return int(match.group(1))
    return None

def is_dynamic_array(input_text):
    pattern = re.compile(r"^[A-Za-z0-9]+\[\]$")
    return pattern.match(input_text) is not None

def is_base_type(input_text):
    pattern = re.compile(r"^[A-Za-z0-9]+")
    match = pattern.match(input_text)
    if match:
        base_type = match.group(0)
        return base_type in BaseTypes
    return False

def add_flags_to_fields(fields: list) -> None:
    for field in fields:
        field_type = field['type']
        field['is_static_array'] = is_static_array(field_type)
        field['is_dynamic_array'] = is_dynamic_array(field_type)
        field['is_base_type'] = is_base_type(field_type)
        field['static_array_size'] = get_static_array_size(field_type)
        field['type_str'] = get_type(field_type)