# encoding: utf-8
import json
import csv
from dataclasses import dataclass
from collections import Counter, OrderedDict, defaultdict
from multiprocessing.pool import ThreadPool as Pool
import os
from functools import reduce
from typing import *
from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path

resources_path = 'files/resources'
operators_path = 'files/operators'
user_operators_path = 'files/csv/user_operators.csv'


def read_json(file_path: str, show: bool = False) -> dict:
    with open(file_path, mode='r', encoding='utf-8') as f:
        print(f"Reading: {file_path}") if show else None
        data = json.load(f)
        f.close()
    return data


resources_data = [read_json(str(path), show=False) for path in Path(resources_path).rglob('*.json')]
operators_data = [read_json(str(path), show=False) for path in Path(operators_path).rglob('*.json')]
df_operators = pd.DataFrame(operators_data)

with open(user_operators_path, mode="r", encoding="utf-8") as f:
    user_operators = [dict(operator) for operator in csv.DictReader(f, delimiter=';')]


@dataclass
class Resource:
    name: str = None
    recipe: list = None


@dataclass
class Operator:
    name: str = None
    stars: int = 0


def calc_operator_resources():
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

    operator_spent_resources = list()
    for user_operator in user_operators:
        operator_info = df_operators.loc[df_operators['name'] == user_operator['name']].to_dict('records')[0]
        skill_resources = sum_skill_upgrade_resources(operator_info['skills']['upgrade'], user_operator)
        elite_resources = sum_elite_upgrade_resources(operator_info['elite'], user_operator)
        mastery_resources = sum_mastery_upgrade_resources(operator_info['skills']['mastery'], user_operator)
        operator_resources = dict(Counter(skill_resources) + Counter(elite_resources) + Counter(mastery_resources))
        operator_spent_resources.append({'operator': operator_info['name'], 'spent_resources': operator_resources})

    # dict(reduce(lambda x, y: Counter(x) + Counter(y), operator_resources_list))
    df_operator_resources = pd.DataFrame(operator_spent_resources).set_index('operator')
    return df_operator_resources


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
        elite1_resources = dict()
        elite2_resources = dict()
        for level in elites:
            for iteration, resource in enumerate(level['resources']):
                key = resource['name']
                value = resource['quantity']
                if level['level'] == 1:
                    elite1_resources[key] = elite1_resources.get(key, 0) + value
                else:
                    elite2_resources[key] = elite2_resources.get(key, 0) + value
                elites_resources[key] = elites_resources.get(key, 0) + value
        return elites_resources, elite1_resources, elite2_resources

    operator_stars = list()
    operator_upgrade_resources = list()
    operator_elite1_resources = list()
    operator_elite2_resources = list()
    operator_elite_resources = list()
    operator_mastery_resources = list()
    operator_total_resources = list()
    for operator in operators_data:
        operator_stars.append({'operator': operator['name'], 'stars': operator['stars']})

        skill_resources = get_operator_resources(operator['skills']['upgrade'])
        operator_upgrade_resources.append({'operator': operator['name'], 'skill_upgrade_resources': skill_resources})

        elite_resources, elite1_resources, elite2_resources = get_elite_resources(operator['elite'])
        operator_elite1_resources.append({'operator': operator['name'], 'elite1_resources': elite1_resources})
        operator_elite2_resources.append({'operator': operator['name'], 'elite2_resources': elite2_resources})
        operator_elite_resources.append({'operator': operator['name'], 'elite_resources': elite_resources})

        mastery_resources = get_mastery_resources(operator['skills']['mastery'])
        operator_mastery_resources.append({'operator': operator['name'], 'mastery_resources': mastery_resources})

        operator_resources = dict(Counter(skill_resources) + Counter(elite_resources) + Counter(mastery_resources))
        operator_total_resources.append({'operator': operator['name'], 'total_resources': operator_resources})

    df_operator_resources = pd.DataFrame(operator_stars).set_index('operator') \
        .join(pd.DataFrame(operator_upgrade_resources).set_index('operator')) \
        .join(pd.DataFrame(operator_elite1_resources).set_index('operator')) \
        .join(pd.DataFrame(operator_elite2_resources).set_index('operator')) \
        .join(pd.DataFrame(operator_elite_resources).set_index('operator')) \
        .join(pd.DataFrame(operator_mastery_resources).set_index('operator')) \
        .join(pd.DataFrame(operator_total_resources).set_index('operator'))
    return df_operator_resources


def calc_resources_needed(global_resources, user_resources) -> dict:
    needed_resources = global_resources.subtract(user_resources, fill_value=0).reset_index().to_dict('records')
    resources = dict()
    for resource in needed_resources:
        resource = list(resource.items())
        resource_name, resource_quantity = resource[0][1], resource[1][1]
        resources[resource_name] = int(resource_quantity)
    return resources


def to_df(resources):
    df = pd.DataFrame(data=resources.items(), columns=["Resource", "Quantity"])
    df = df.astype({'Resource': 'string', 'Quantity': 'int32'})
    df.sort_values(by=['Resource'], inplace=True)
    df.reset_index(inplace=True, drop=True)
    df.set_index('Resource', inplace=True)
    return df


def get_needed_resources(row):
    resources = dict(Counter(row['total_resources']) - Counter(row['spent_resources']))
    return None if len(resources) == 0 else resources


def sum_material(resources):
    if resources is None:
        return 0
    resources.pop('LMD', None)
    return sum(resources.values())


def format_resources(row):
    return None if row is None else '\n'.join([f'{value}x {key}' for key, value in row.items()])


if __name__ == "__main__":
    today = str(datetime.today()).split()[0]
    reports_path = f'files/reports/{today}'
    spent_filepath = f'{reports_path}/total-spent-resources.csv'
    operators_filepath = f'{reports_path}/total-operators-resources.csv'
    needed_filepath = f'{reports_path}/total-needed-resources.csv'
    sheet_path = f'{reports_path}/report.xlsx'
    Path(reports_path).mkdir(parents=True, exist_ok=True)

    print("Global resources.")
    global_resources = calc_global_resources()
    # global_resources

    print("User total resources.")
    spent_resources = calc_operator_resources()
    resume = global_resources.join(spent_resources)
    resume['needed_resources'] = resume.apply(get_needed_resources, axis=1)
    resume['needed_material_quantity'] = resume.apply(lambda row: sum_material(row['needed_resources']), axis=1)
    resume['total_material_quantity'] = resume.apply(lambda row: sum_material(row['total_resources']), axis=1)
    resume['percentage'] = (resume['total_material_quantity'] - resume['needed_material_quantity']) / resume[
        'total_material_quantity']
    resume = resume.round(4)
    resume['percentage'] = (resume['percentage'] * 100).astype('string') \
        .str.pad(width=4, fillchar='0', side='left') \
        .str.pad(width=10, fillchar='0', side='right') \
        .str.slice(start=0, stop=5).astype('float64')
    resume.sort_values(by=['percentage', 'stars'], inplace=True, ascending=False)
    for resource_column in ['skill_upgrade_resources', 'elite1_resources', 'elite2_resources', 'elite_resources',
                            'mastery_resources', 'total_resources', 'spent_resources', 'needed_resources']:
        resume[resource_column] = resume.apply(lambda row: format_resources(row[resource_column]), axis=1)
    resume = resume.fillna('None')
    column_order = ['percentage', 'stars', 'skill_upgrade_resources', 'elite1_resources',
                    'elite2_resources', 'elite_resources', 'mastery_resources', 'total_resources', 'spent_resources',
                    'needed_resources', 'needed_material_quantity', 'total_material_quantity']
    resume = resume[column_order]
    # resume['needed_lmd'] = resume.apply(lambda row: row['needed_resources']['lmd'], axis=1)
    # resume['total_lmd'] = resume.apply(lambda row: row['total_resources']['lmd'], axis=1)
    resume.to_csv('files/reports/global_resources.csv', sep=';')
    # user_resources = to_df(calc_user_total_resources(user_operators)) \
    #     .reindex_like(global_resources) \
    #     .fillna(0) \
    #     .reset_index() \
    #     .astype({'Resource': 'string', 'Quantity': 'int32'}) \
    #     .set_index('Resource')
    #
    # print("Needed resources.")
    # needed_resources = to_df(calc_resources_needed(global_resources, user_resources))

    # print("Creating Resume.")
    # resume = calc_resume(global_resources, user_resources, needed_resources)
    # print(resume)

    # TODO: Testes Unitários https://www.youtube.com/watch?v=6tNS--WetLI&ab_channel=CoreySchafer
    # TODO: Adicionar tier no dataframe de resumo
    # TODO: Calculo de recursos para fabricação de recurso tier 5
    # TODO: calculo de lmd necessario na fabricação
    # TODO: Estimar quantidade de LMD e passes de XP para LVL Maximo E0 E1 E2
    # TODO: Coluna Total LMD Elites1 e 2
    # TODO: Coluna Total Passes de XP amarelos LVL
    # TODO: Coluna total de LMD e recursos após fabricacao
