# encoding: utf-8
import json
import csv
from dataclasses import dataclass
from collections import Counter
from multiprocessing.pool import ThreadPool as Pool

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


def sum_mastery_upgrade_resources(upgrades, user_op):
    resources = dict()
    for skill_mastery in upgrades:
        # sai do laco se a skill nao tem maestria
        if int(user_op[f's{skill_mastery["skill"]}_mastery']) <= 0:
            break
        for level in skill_mastery['upgrade']:
            if level['level'] > int(user_op[f's{skill_mastery["skill"]}_mastery']):
                break
            for resource in level['resources']:
                key = resource['name']
                value = resource['quantity']
                resources[key] = resources.get(key, 0) + value
    return resources


def sum_elite_upgrade_resources(upgrades, user_op):
    resources = dict()
    for level in upgrades:
        if level['level'] > int(user_op['elite']):
            break
        for iteration, resource in enumerate(level['resources']):
            key = resource['name']
            value = resource['quantity']
            resources[key] = resources.get(key, 0) + value
    return resources


def calc_operator_resources(operator: dict):
    resources = dict()
    for op in operators_data:
        if operator['name'] in op['name']:
            skill_resources = sum_skill_upgrade_resources(op['skills']['upgrade'], operator)
            elite_resources = sum_elite_upgrade_resources(op['elite'], operator)
            mastery_resources = sum_mastery_upgrade_resources(op['skills']['mastery'], operator)
            resources = Counter(skill_resources) + Counter(elite_resources) + Counter(mastery_resources)
    return resources


def calc_total_resources(operators):
    from functools import reduce
    resources = dict()
    with Pool(8) as p:
        operator_resources_list = p.map(calc_operator_resources, operators)
    operator_resources_list = [calc_operator_resources(operator) for operator in operators]
    return dict(reduce(lambda x, y: Counter(x) + Counter(y), operator_resources_list))


if __name__ == "__main__":
    with open(user_operators_path, mode="r", encoding="utf-8") as f:
        operators = [dict(operator) for operator in csv.DictReader(f, delimiter=';')]
        f.close()
    print(calc_total_resources(operators))
