# encoding: utf-8
import json
import pandas as pd
from dataclasses import dataclass


def read_json(file_path: str) -> dict:
    with open(file_path, mode='r', encoding='utf-8') as f:
        print(f"Validating json: {file_path}")
        data = json.load(f)
        f.close()
    return data


@dataclass
class Resource:
    name: str = None
    recipe: list = None


@dataclass
class Operator:
    name: str = None
    stars: int = 0


if __name__ == "__main__":
    resources_path = 'files/resource.json'
    # data = read_json(resources_path)
    df_resources = pd.read_json(resources_path)
    print(df_resources)
    # print(json.dumps(data, indent=4, sort_keys=True))


