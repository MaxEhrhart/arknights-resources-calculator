# encoding: utf-8
from collections import Counter
from datetime import datetime, date
from enum import Enum
from functools import reduce
from pathlib import Path
from typing import *

import numpy as np
import pandas as pd
import pytz
from pandas_xlsx_tables import df_to_xlsx_table

from arknights.operator import load_operators
from arknights.resource import get_resources_data


class Constants(Enum):
    REPORTS_PATH: Path = Path(f'files/reports')
    TODAY: date = datetime.now(pytz.timezone('America/Sao_Paulo')).date()


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
    Constants.REPORTS_PATH.value.mkdir(parents=True, exist_ok=True)
    report_path = f'{Constants.REPORTS_PATH.value}/{Constants.TODAY.value}-resources-by-operator.xlsx'
    print("Global resources.")
    resume = pd.DataFrame(list(map(lambda op: op.to_dict(), operators))) \
        .rename(columns={"name": "operator"}) \
        .set_index('operator') \
        .sort_values(by=['stars', 'operator', 'material_percentage'], ascending=False)

    resource_columns = [column for column in resume.columns if 'resource' in column]
    for resource_column in resource_columns:
        resume[resource_column] = resume.apply(lambda row: operator_format_resources(row[resource_column]), axis=1)
    column_order = [
        'overall_percentage',
        'material_percentage',
        'lmd_percentage',
        'yellow_exp_percentage',
        'stars',
        'elite',
        'skill_level',
        's1_mastery',
        's2_mastery',
        's3_mastery',
        'elite_resources',
        'mastery_resources',
        'spent_resources',
        'needed_elite_resources',
        'needed_mastery_resources',
        'needed_skill_resources',
        'needed_resources',
        'needed_material_quantity',
        'total_material_quantity',
        'spent_yellow_exp',
        'needed_yellow_exp',
        'spent_lmd',
        'needed_lmd',
        'total_yellow_exp',
        'total_lmd'
    ]
    resume = resume[column_order]
    resume.to_excel(report_path)
    print(f"Report saved at {report_path}")


def get_operator_attribute_resource(attribute):
    _resources = [getattr(operator, attribute) for operator in operators]
    _resources = dict(reduce(lambda x, y: Counter(x) + Counter(y), _resources))
    df = pd.DataFrame(data=_resources.items(), columns=["Resource", "Quantity"]) \
        .astype({'Resource': 'string', 'Quantity': 'int32'}) \
        .set_index('Resource')
    return df


def resources_report():
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
    save_as_xlsx(resume, f'{report_path}/{Constants.TODAY.value}-resources-report.xlsx', show=True)
    print(f"Report saved at {report_path}/{Constants.TODAY.value}-resources-report.xlsx")


def needed_resource():
    Constants.REPORTS_PATH.value.mkdir(parents=True, exist_ok=True)
    report_path = f'{Constants.REPORTS_PATH.value}/{Constants.TODAY.value}-operator_needed_resource.xlsx'
    index_columns = ['operator', 'stars', 'elite', 'level', 'skill_level', 'overall_percentage']
    resume = pd.DataFrame(list(map(lambda op: op.to_dict(), operators))).rename(columns={"name": "operator"})
    # resume = resume[(resume.overall_percentage > 0) & (resume.overall_percentage < 100)]
    resume = resume.set_index(keys=index_columns)
    resume = resume[['needed_resources', 'needed_lmd', 'needed_yellow_exp']]
    resume = pd.concat([resume.drop(['needed_resources'], axis=1), resume.needed_resources.apply(pd.Series)], axis=1)
    resume = resume.rename(columns={'needed_yellow_exp': 'Yellow Exp'})
    resume = resume.fillna(0)
    resume['LMD'] = resume['LMD'] + resume['needed_lmd']
    resume.drop(['needed_lmd'], axis=1, inplace=True)
    resume = resume.reindex(sorted(resume.columns), axis=1)
    resume = resume.sort_values(by=['overall_percentage', 'stars', 'elite', 'skill_level', 'level', 'operator'])
    resume = resume.astype('int64')
    resume = resume.replace(0, np.nan)
    df_to_xlsx_table(
        df=resume,
        table_name='NeededResources',
        file=report_path,
        header_orientation="diagonal",
        table_style="Table Style Light 9"
    )
    print(f"Report saved at {report_path}")


def spent_resource():
    Constants.REPORTS_PATH.value.mkdir(parents=True, exist_ok=True)
    report_path = f'{Constants.REPORTS_PATH.value}/{Constants.TODAY.value}-operator_spent_resource.xlsx'
    index_columns = ['operator', 'stars', 'elite', 'level', 'skill_level', 'overall_percentage']
    resume = pd.DataFrame(list(map(lambda op: op.to_dict(), operators))).rename(columns={"name": "operator"})
    # resume = resume[resume.overall_percentage > 0]
    resume = resume.set_index(keys=index_columns)
    resume = resume[['spent_resources', 'spent_lmd', 'spent_yellow_exp', 'spent_elite_lmd']]
    resume = pd.concat([resume.drop(['spent_resources'], axis=1), resume.spent_resources.apply(pd.Series)], axis=1)
    resume = resume.rename(columns={'spent_yellow_exp': 'Yellow Exp'})
    resume = resume.fillna(0)
    resume['LMD'] = resume['spent_elite_lmd'] + resume['spent_lmd']
    resume.drop(['spent_lmd', 'spent_elite_lmd'], axis=1, inplace=True)
    resume = resume.reindex(sorted(resume.columns), axis=1)
    resume = resume.sort_values(by=['overall_percentage', 'stars', 'elite', 'skill_level', 'level', 'operator'])
    resume = resume.astype('int64')
    resume = resume.replace(0, np.nan)
    df_to_xlsx_table(
        df=resume,
        table_name='SpentResources',
        file=report_path,
        header_orientation="diagonal",
        table_style="Table Style Light 9"
    )
    print(f"Report saved at {report_path}")


if __name__ == '__main__':
    print("Generating resources report")
    resources_report()
    print("Generating resources report: done")
    print(40*"#")
    print("Generating needed_resource report")
    needed_resource()
    print("Generating needed_resource report: done")
    print(40*"#")
    print("Generating spent_resource report")
    spent_resource()
    print("Generating spent_resource report: done")


# TODO: Testes Unitários https://www.youtube.com/watch?v=6tNS--WetLI&ab_channel=CoreySchafer
# TODO: Calculo de recursos para fabricação de recurso tier 5
# TODO: calculo de lmd necessario na fabricação
# TODO: Coluna total de LMD recursos após fabricacao - Soma dos custo total em lmd de fabricacao mais os a quantidade
