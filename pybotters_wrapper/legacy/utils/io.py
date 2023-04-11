from __future__ import annotations

import json
import os


def read_json(path: str):
    with open(path) as f:
        return json.load(f)


def write_json(path: str, obj: any):
    with open(path, "w") as f:
        json.dump(obj, f, indent=4)


RESOURCE_PATH = os.path.join(os.path.dirname(__file__), "../resources")


def read_resource(filename):
    filepath = os.path.join(RESOURCE_PATH, filename)
    if filename.endswith(".json"):
        return read_json(filepath)
    else:
        with open(filepath) as f:
            return f.readlines()
