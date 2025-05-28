import re
from base_types import BaseTypes


def is_valid(input_text):
    if input_text is None:
        return None
    pattern = re.compile(
        r"^([a-zA-Z_][a-zA-Z0-9_]*\[([0-9]*|[a-zA-Z_][a-zA-Z0-9_]*)\]|[a-zA-Z_][a-zA-Z0-9_]*|[a-zA-Z_][a-zA-Z0-9_]+)$"
    )
    return pattern.match(input_text) is not None


def get_value_type(input_text):
    if input_text is None:
        return None
    pattern = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)(?:\[[a-zA-Z0-9_]*\])?$")
    match = pattern.search(input_text)
    if match:
        return match.group(1)
    return None


def get_key_type(input_text):
    if input_text is None:
        return None
    pattern = re.compile(r"^(?:[a-zA-Z_][a-zA-Z0-9_]*)(?:\[)([a-zA-Z_][a-zA-Z0-9_]*)(?:\])$")
    match = pattern.search(input_text)
    if match:
        return match.group(1)
    return None


def is_map(input_text):
    if input_text is None:
        return None
    pattern = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*\[[a-zA-Z_][a-zA-Z0-9_]*\]$")
    return pattern.match(input_text) is not None


def is_array(input_text):
    if input_text is None:
        return None
    # return is_static_array(input_text) or is_dynamic_array(input_text)
    pattern = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*\[[0-9]*\]$")
    return pattern.match(input_text) is not None


def is_static_array(input_text):
    if input_text is None:
        return None
    pattern = re.compile(r"^[A-Za-z0-9]+\[[0-9]+\]$")
    return pattern.match(input_text) is not None


def get_static_array_size(input_text):
    if input_text is None:
        return None
    pattern = re.compile(r"\[([0-9]+)\]$")
    match = pattern.search(input_text)
    if match:
        return int(match.group(1))
    return None


def is_dynamic_array(input_text):
    if input_text is None:
        return None
    pattern = re.compile(r"^[A-Za-z0-9]+\[\]$")
    return pattern.match(input_text) is not None


def is_base_type(input_text):
    if input_text is None:
        return None
    pattern = re.compile(r"^[A-Za-z0-9]+")
    match = pattern.match(input_text)
    if match:
        base_type = match.group(0)
        return base_type in BaseTypes
    return False


def add_flags_to_fields(fields: list) -> None:
    for field in fields:
        field_type = field["type"]
        field["is_static_array"] = is_static_array(field_type)
        field["is_dynamic_array"] = is_dynamic_array(field_type)
        field["is_map"] = is_map(field_type)
        field["value_type"] = get_value_type(field_type)
        field["key_type"] = get_key_type(field_type)
        field["value_type_is_base"] = is_base_type(field["value_type"])
        field["key_type_is_base"] = is_base_type(field["key_type"])
        field["static_array_size"] = get_static_array_size(field_type)
