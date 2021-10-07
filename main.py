# encoding: utf-8
import json
import csv
# import pandas as pd
from dataclasses import dataclass

resources_path = 'files/resource.json'
operators_path = 'files/operator.json'
user_operators_path = 'files/user_operators.csv'


def read_json(file_path: str) -> dict:
    with open(file_path, mode='r', encoding='utf-8') as f:
        print(f"Validating json: {file_path}")
        data = json.load(f)
        f.close()
    return data


resources_data = read_json(resources_path)
operators_data = read_json(operators_path)


@dataclass
class Resource:
    name: str = None
    recipe: list = None


@dataclass
class Operator:
    name: str = None
    stars: int = 0


def sum_skill_upgrade_resources(upgrades, user_op):
    resources = dict()
    for level in upgrades:
        if level['level'] > int(user_op['skill_level']):
            break
        for iteration, resource in enumerate(level['resources']):
            key = resource['name']
            value = resource['quantity']
            resources[key] = resources.get(key, 0) + value
    return resources


def calc_resource(operator: dict):
    resources = dict()
    for op in operators_data:
        if operator['operator'] in op['name']:
            resources = {**resources, **sum_skill_upgrade_resources(op['skills']['upgrade'], operator)}
    print(operator['operator'], resources)


if __name__ == "__main__":
    with open(user_operators_path, mode="r", encoding="utf-8") as f:
        csv_reader = csv.DictReader(f, delimiter=';')
        for operator in csv_reader:
            calc_resource(operator)


# df_resources = pd.read_json(resources_path)
# df_operators = pd.read_json(operators_path)
# print(df_resources)
# print(df_operators)
