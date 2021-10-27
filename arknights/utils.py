import json


def read_json(file_path: str, show: bool = False) -> dict:
    with open(file_path, mode='r', encoding='utf-8') as f:
        print(f"Reading: {file_path}") if show else None
        data = json.load(f)
        f.close()
    return data
