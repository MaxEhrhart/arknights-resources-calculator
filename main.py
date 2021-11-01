# encoding: utf-8
from collections import Counter
from datetime import datetime
from functools import reduce
from pathlib import Path
from typing import *

import numpy as np
import pandas as pd

from arknights.operator import load_operators
from arknights.resource import get_resources_data

operators = load_operators('files/user_operators.csv')
df_resources = pd.DataFrame(get_resources_data()) \
    .rename(columns={'name': 'Resource'}) \
    .set_index('Resource')


def calc_resume(df1, df2, df3) -> pd.DataFrame:
    renamed_columns = {'Resource': 'Resource', 'Quantity_global': 'Total', 'Quantity_spent': 'Spent',
                       'Quantity': 'Needed', 'tier': 'Tier', 'droppable': 'Droppable', 'lmd': 'LMD'}
    columns_order = ['Tier', 'LMD', 'Droppable', 'Total', 'Spent', 'Needed']
    resume = df1 \
        .join(df2, lsuffix='_global', rsuffix='_spent') \
        .join(df3, lsuffix='_global', rsuffix='_needed') \
        .join(df_resources, lsuffix='_global', rsuffix='_resources') \
        .rename(columns=renamed_columns)[columns_order] \
        .sort_values(by=['Resource', 'Tier'])
    resume['Percentage'] = np.round(resume['Spent'] / resume['Total'], decimals=4)
    return resume


# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(df.head(500)) if show else None

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
    totals_functions = {
        'resource': None,
        'percentage': 'average',
        'total': None,
        'spent': None,
        'needed': None,
        'tier': None,
        'lmd': None,
        'droppable': None
    }
    column_settings = [
        {'header': column, 'total_function': totals_functions[column.lower()]} for column in df.columns
    ]
    options = {'columns': column_settings,
               'style': 'Table Style Light 15',
               'first_column': True,
               'last_column': True,
               'total_row': True}
    worksheet.add_table(0, 0, max_row + 1, max_col - 1, options)

    for i, width in enumerate(col_widths):
        worksheet.set_column(i, i, width)
    percent_fmt = workbook.add_format({'num_format': '0.00%'})
    worksheet.set_column('H:H', None, percent_fmt)

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()


def operator_format_resources(row):
    return None if row is None else '\n'.join([f'{value}x {key}' for key, value in row.items()])


def resources_by_operator_report():
    today = str(datetime.today()).split()[0]
    reports_path = f'files/reports'
    Path(reports_path).mkdir(parents=True, exist_ok=True)

    print("Global resources.")
    resume = pd.DataFrame(list(map(lambda op: op.to_dict(), operators))) \
        .rename(columns={"name": "operator"}) \
        .set_index('operator') \
        .sort_values(by=['stars', 'operator', 'material_percentage'], ascending=False)

    resource_columns = [column for column in resume.columns if 'resource' in column]
    for resource_column in resource_columns:
        resume[resource_column] = resume.apply(lambda row: operator_format_resources(row[resource_column]), axis=1)
    column_order = [
        'material_percentage',
        'stars',
        'elite',
        'skill_level',
        's1_mastery',
        's2_mastery',
        's3_mastery',
        'skill_upgrade_resources',
        'elite1_resources',
        'elite2_resources',
        'elite_resources',
        'mastery_resources',
        'total_resources',
        'spent_resources',
        'needed_resources',
        'needed_material_quantity',
        'total_material_quantity'
    ]
    resume = resume[column_order]
    # resume['needed_lmd'] = resume.apply(lambda row: row['needed_resources']['lmd'], axis=1)
    # resume['total_lmd'] = resume.apply(lambda row: row['total_resources']['lmd'], axis=1)
    today = str(datetime.today()).split()[0]
    report_path = f'{reports_path}/{today}-resources-by-operator-report.csv'
    resume.to_csv(report_path, sep=';')
    print(f"Report saved at {report_path}")


def get_operator_attribute_resource(attribute):
    _resources = [getattr(operator, attribute) for operator in operators]
    _resources = dict(reduce(lambda x, y: Counter(x) + Counter(y), _resources))
    df = pd.DataFrame(data=_resources.items(), columns=["Resource", "Quantity"]) \
        .astype({'Resource': 'string', 'Quantity': 'int32'}) \
        .set_index('Resource')
    return df


def resources_report():
    today = str(datetime.today()).split()[0]
    report_path = f'files/reports'
    Path(report_path).mkdir(parents=True, exist_ok=True)

    print("Global resources.")
    total_resources = get_operator_attribute_resource('total_resources')

    print("Spent resources.")
    spent_resources = get_operator_attribute_resource('spent_resources') \
        .reindex_like(total_resources) \
        .fillna(0)

    print("Needed resources.")
    needed_resources = get_operator_attribute_resource('needed_resources') \
        .reindex_like(total_resources) \
        .fillna(0)

    resume = calc_resume(total_resources, spent_resources, needed_resources)

    print("Saving as xlsx.")
    save_as_xlsx(resume, f'{report_path}/{today}-resources-report.xlsx', show=True)
    print(f"Report saved at {report_path}")


if __name__ == '__main__':
    print("Generating resources report")
    resources_report()
    print("Generating resources report: done")
    print("Generating resources by operator report")
    resources_by_operator_report()
    print("Generating resources by operator report: done")

# TODO: Testes Unitários https://www.youtube.com/watch?v=6tNS--WetLI&ab_channel=CoreySchafer
# TODO: Calculo de recursos para fabricação de recurso tier 5
# TODO: calculo de lmd necessario na fabricação
# TODO: Estimar quantidade de LMD e passes de XP para LVL Maximo E0 E1 E2
# TODO: Coluna Total LMD Elites1 e 2
# TODO: Coluna Total Passes de XP amarelos LVL
# TODO: Coluna total de LMD e recursos após fabricacao
