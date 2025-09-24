from jsonschema import validate, ValidationError
import json
from hashlib import md5
import re
from typing import Any

Json = dict[str, Any]

def get_schema(json_file: str) -> Json:
    """
    Get the JSON schema from a file.
    """
    with open(json_file, "r") as f:
        return json.load(f)


def get_hash(pathname: str) -> str:
    """
    Get the MD5 hash of a file, ignoring whitespace.
    """
    with open(pathname, "r") as f:
        file_str = f.read()
        file_str = re.sub(r"\s+", "", file_str, flags=re.UNICODE)
        return md5(file_str.encode()).hexdigest()


def write_to_file(filepath: str, data: Json) -> None:
    """
    Write JSON data to a file.
    """
    with open(filepath, "w") as f:
        f.write(json.dumps(data, indent=2))


def validate_json(json_file: str, schema: Any) -> Json | None:
    """
    Validate a JSON file against a schema.
    """
    with open(json_file, "r") as f:
        try:
            data = json.load(f)
            validate(data, schema)
            return data
        except ValidationError as e:
            print(e.message)
            return None
    return None


def get_dict_from_json(json_file: str) -> Json:
    """
    Get a dictionary from a JSON file.
    """
    with open(json_file, "r") as f:
        return json.load(f)
