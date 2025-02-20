from jsonschema import validate
import json
from hashlib import md5

def get_schema(json_file: str) -> dict:
    with open(json_file, 'r') as f:
        return json.load(f)

def get_hash(msg: dict) -> str:
    return md5(json.dumps(msg, sort_keys=True).encode()).hexdigest()

def write_to_file(filepath: str, data: dict) -> None:
    with open(filepath, 'w') as f:
        f.write(json.dumps(data, indent=2))

def validate_json(json_file: str, schema: dict) -> dict:
    with open(json_file, 'r') as f:
        data = json.load(f)
        validate(data, schema)
        return data
