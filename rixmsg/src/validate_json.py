from jsonschema import validate, ValidationError
import json
from hashlib import md5


def get_schema(json_file: str) -> dict:
    with open(json_file, "r") as f:
        return json.load(f)


def get_hash(pathname: str) -> str:
    with open(pathname, "r") as f:
        return md5(f.read().encode()).hexdigest()


def write_to_file(filepath: str, data: dict) -> None:
    with open(filepath, "w") as f:
        f.write(json.dumps(data, indent=2))


def validate_json(json_file: str, schema: dict) -> dict | None:
    with open(json_file, "r") as f:
        try:
            data = json.load(f)
            validate(data, schema)
            return data
        except ValidationError as e:
            print(e.message)
            return None
    return None

def get_dict_from_json(json_file: str) -> dict:
    with open(json_file, "r") as f:
        return json.load(f)