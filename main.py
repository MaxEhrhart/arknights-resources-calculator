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

resources_path = 'files/resource.json'
operators_path = 'files/operators'
user_operators_path = 'files/csv/user_operators.csv'


def read_json(file_path: str, show: bool = False) -> dict:
    with open(file_path, mode='r', encoding='utf-8') as f:
        print(f"Validating operators: {file_path}") if show else None
        data = json.load(f)
        f.close()
    return data


resources_data = read_json(resources_path)
operators_data = [read_json(str(path), show=False) for path in Path(operators_path).rglob('*.json')]


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
    with Pool(12) as p:
        operator_resources_list = p.map(calc_operator_resources, operators)
    # operator_resources_list = [calc_operator_resources(operator) for operator in operators]
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


def calc_resources_needed(global_resources, user_resources) -> dict:
    needed_resources = global_resources.subtract(user_resources, fill_value=0).reset_index().to_dict('records')
    resources = dict()
    for resource in needed_resources:
        resource = list(resource.items())
        resource_name, resource_quantity = resource[0][1], resource[1][1]
        resources[resource_name] = int(resource_quantity)
    return resources


def calc_resume(df1, df2, df3) -> pd.DataFrame:
    renamed_columns = {'Resource': 'Resource', 'Quantity_global': 'Total', 'Quantity_spent': 'Spent',
                      'Quantity': 'Needed'}
    columns_order = ['Total', 'Spent', 'Needed']
    resume = df1 \
        .join(df2, lsuffix='_global', rsuffix='_spent') \
        .join(df3, lsuffix='_global', rsuffix='_needed') \
        .rename(columns=renamed_columns)[columns_order]
    resume['Percentage'] = np.round(resume['Spent'] / resume['Total'], decimals=4)
    return resume


def save_as_csv(resources, file_path, show: bool = False) -> pd.DataFrame:
    df = pd.DataFrame(data=resources.items(), columns=["Resource", "Quantity"])
    df = df.astype({'Resource': 'string', 'Quantity': 'int32'})
    df.sort_values(by=['Resource'], inplace=True)
    df.reset_index(inplace=True, drop=True)
    df.to_csv(file_path, sep=';', header=True, encoding='utf8', index=False)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df.head(500)) if show else None
    return df


def save_as_xlsx(df, file_path, show: bool = False):
    def get_col_widths(dataframe):
        # First we find the maximum length of the index column
        idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
        # Then, we concatenate this to the max of the lengths of column
        # name and its values for each column, left to right
        return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]

    col_widths = get_col_widths(df)
    df = df.reset_index()

    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    workbook = writer.book
    worksheet = workbook.add_worksheet('Comparison')
    writer.sheets['Comparison'] = worksheet
    df.to_excel(writer, sheet_name='Comparison', startrow=0, startcol=0, index=False)

    (max_row, max_col) = df.shape
    column_settings = [{'header': column} for column in df.columns]
    worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings,
                                                     'style': 'Table Style Light 15', 'first_column': True,
                                                     'last_column': True})
    for i, width in enumerate(col_widths):
        worksheet.set_column(i, i, width)
    percent_fmt = workbook.add_format({'num_format': '0.00%'})
    worksheet.set_column('E:E', None, percent_fmt)

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()


if __name__ == "__main__":
    today = str(datetime.today()).split()[0]
    reports_path = f'files/reports/{today}'
    spent_filepath = f'{reports_path}/total-spent-resources.csv'
    operators_filepath = f'{reports_path}/total-operators-resources.csv'
    needed_filepath = f'{reports_path}/total-needed-resources.csv'
    sheet_path = f'{reports_path}/report.xlsx'
    Path(reports_path).mkdir(parents=True, exist_ok=True)

    with open(user_operators_path, mode="r", encoding="utf-8") as f:
        operators = [dict(operator) for operator in csv.DictReader(f, delimiter=';')]

    print("Global resources.")
    global_resources = save_as_csv(calc_global_resources(), operators_filepath, show=False) \
        .set_index('Resource')

    print("User total resources.")
    user_resources = save_as_csv(calc_user_total_resources(operators), spent_filepath, show=False) \
        .set_index('Resource') \
        .reindex_like(global_resources) \
        .fillna(0) \
        .reset_index() \
        .astype({'Resource': 'string', 'Quantity': 'int32'}) \
        .set_index('Resource')

    print("Needed resources.")
    resources_needed = calc_resources_needed(global_resources, user_resources)
    needed_resources = save_as_csv(resources_needed, needed_filepath, show=False).set_index('Resource')

    print("Creating Resume.")
    resume = calc_resume(global_resources, user_resources, needed_resources)

    print("Saving as xlsx.")
    save_as_xlsx(resume, sheet_path, show=True)
    print(f"Report saved at {sheet_path}")


# TODO: Adicionar tier no dataframe de resumo
# TODO: Calculo de recursos para fabricação de recurso tier 5
# TODO: calculo de lmd necessario na fabricação
# TODO: Estimar quantidade de LMD e passes de XP para LVL Maximo E0 E1 E2
# TODO: Coluna Total LMD Elites
# TODO: Coluna Total Passes de XP amarelos LVL
# TODO: Coluna total de LMD e recursos após fabricacao


