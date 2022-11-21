import json


def read_json(path: str):
    with open(path) as f:
        return json.load(f)


def write_json(path: str, obj: any):
    with open(path, "w") as f:
        json.dump(obj, f, indent=4)

