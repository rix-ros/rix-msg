import re
from base_types import BaseTypes


def is_valid(input_text: str | None) -> bool:
    """
    Check if the input text is a valid type.
    A valid type is one of the following:
        - A base type (e.g. int32, string, etc.)
        - A custom type (e.g. MyMessage)
        - A static array (e.g. int32[10], MyMessage[5], etc.)
        - A dynamic array (e.g. int32[], MyMessage[], etc.)
    """
    if input_text is None:
        return False
    pattern = re.compile(r"^([a-zA-Z][a-zA-Z0-9_]*\[([0-9]*)\]|[a-zA-Z][a-zA-Z0-9_]*)$")
    return pattern.match(input_text) is not None


def get_value_type(input_text: str | None) -> str | None:
    """
    Get the value type from the input text.
    For example:
        - int32[10] -> int32
        - MyMessage[5] -> MyMessage
        - int32[] -> int32
        - MyMessage[] -> MyMessage
        - int32[string] -> int32
        - MyMessage[int32] -> MyMessage
        - int32 -> int32
        - MyMessage -> MyMessage
    """
    if input_text is None:
        return None
    pattern = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)(?:\[[a-zA-Z0-9_]*\])?$")
    match = pattern.search(input_text)
    if match:
        return match.group(1)
    return None


def is_static_array(input_text: str | None) -> bool:
    """
    Check if the input text is a static array type.
    """
    if input_text is None:
        return False
    pattern = re.compile(r"^[A-Za-z0-9]+\[[0-9]+\]$")
    return pattern.match(input_text) is not None


def get_static_array_size(input_text: str | None) -> int | None:
    """
    Get the size of a static array from the input text.
    For example:
        - int32[10] -> 10
        - MyMessage[5] -> 5
        - int32[] -> None
        - MyMessage[] -> None
        - int32[string] -> None
    """
    if input_text is None:
        return None
    pattern = re.compile(r"\[([0-9]+)\]$")
    match = pattern.search(input_text)
    if match:
        return int(match.group(1))
    return None


def is_dynamic_array(input_text: str | None) -> bool:
    """
    Check if the input text is a dynamic array type.
    """
    if input_text is None:
        return False
    pattern = re.compile(r"^[A-Za-z0-9]+\[\]$")
    return pattern.match(input_text) is not None


def is_base_type(input_text: str | None) -> bool:
    """
    Check if the input text is a base type.
    A base type is one of the following:
        - char
        - int8
        - int16
        - int32
        - int64
        - uint8
        - uint16
        - uint32
        - uint64
        - float
        - double
        - bool
        - string
        - pointer
    """
    if input_text is None:
        return False
    pattern = re.compile(r"^[A-Za-z0-9]+")
    match = pattern.match(input_text)
    if match:
        base_type = match.group(0)
        return base_type in BaseTypes
    return False
