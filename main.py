# encoding: utf-8
import json
import csv
from dataclasses import dataclass
from collections import Counter, OrderedDict
# from multiprocessing.pool import ThreadPool as Pool
import os
from functools import reduce
from typing import *


resources_path = 'files/resource.json'
operators_path = 'files/json'
user_operators_path = 'files/csv/user_operators.csv'


def read_json(file_path: str) -> dict:
    with open(file_path, mode='r', encoding='utf-8') as f:
        print(f"Validating json: {file_path}")
        data = json.load(f)
        f.close()
    return data


resources_data: dict = read_json(resources_path)
operators_data: List[dict] = [read_json(operators_path + "/" + file) for file in os.listdir(operators_path)]


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
        if operator['name'].upper() == op['name'].upper():
            skill_resources = sum_skill_upgrade_resources(op['skills']['upgrade'], operator)
            elite_resources = sum_elite_upgrade_resources(op['elite'], operator)
            mastery_resources = sum_mastery_upgrade_resources(op['skills']['mastery'], operator)
            resources = Counter(skill_resources) + Counter(elite_resources) + Counter(mastery_resources)
            # print(operator['name'], resources, sep=": ")
    return resources


def calc_user_total_resources(operators):
    resources = dict()
    # with Pool(8) as p:
    #     operator_resources_list = p.map(calc_operator_resources, operators)
    operator_resources_list = [calc_operator_resources(operator) for operator in operators]
    return dict(reduce(lambda x, y: Counter(x) + Counter(y), operator_resources_list))


def calc_global_resources():
    def get_operator_resources(upgrades) -> dict:
        upgrades_resources = dict()
        for level in upgrades:
            for iteration, resource in enumerate(level['resources']):
                key = resource['name']
                value = resource['quantity']
                upgrades_resources[key] = upgrades_resources.get(key, 0) + value
        return upgrades_resources

    def get_mastery_resources(masteries) -> dict:
        masteries_resources = dict()
        for skill_mastery in masteries:
            for level in skill_mastery['upgrade']:
                for resource in level['resources']:
                    key = resource['name']
                    value = resource['quantity']
                    masteries_resources[key] = masteries_resources.get(key, 0) + value
        return masteries_resources

    def get_elite_resources(elites) -> dict:
        elites_resources = dict()
        for level in elites:
            for iteration, resource in enumerate(level['resources']):
                key = resource['name']
                value = resource['quantity']
                elites_resources[key] = elites_resources.get(key, 0) + value
        return elites_resources

    operator_resources_list = list()
    for operator in operators_data:
        skill_resources = get_operator_resources(operator['skills']['upgrade'])
        elite_resources = get_elite_resources(operator['elite'])
        mastery_resources = get_mastery_resources(operator['skills']['mastery'])
        operator_resources = Counter(skill_resources) + Counter(elite_resources) + Counter(mastery_resources)
        operator_resources_list.append(operator_resources)
    return dict(reduce(lambda x, y: Counter(x) + Counter(y), operator_resources_list))


def calc_resources_needed():
    resources = dict()
    return resources


if __name__ == "__main__":
    with open(user_operators_path, mode="r", encoding="utf-8") as f:
        operators = [dict(operator) for operator in csv.DictReader(f, delimiter=';')]

    print("User total resources:")
    total_resources = OrderedDict(sorted(calc_user_total_resources(operators).items()))
    [print(resource, quantity, sep=": ") for resource, quantity in total_resources.items()]

    print("Global resources:")
    global_resources = OrderedDict(sorted(calc_global_resources().items()))
    [print(resource, quantity, sep=": ") for resource, quantity in global_resources.items()]

    # print("Resources Needed:")
    # [print(resource, quantity, sep=": ") for resource, quantity in calc_resources_needed().items()]
