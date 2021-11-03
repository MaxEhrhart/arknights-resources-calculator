# encoding: utf-8
import csv
from enum import Enum

import pkg_resources

with open(pkg_resources.resource_filename(__name__, "resources/explmd.csv"), mode="r", encoding="utf-8") as f:
    lmd_exp_data = [dict(user_operator) for user_operator in csv.DictReader(f, delimiter=';')]
    # criar campo acumulado até atual
    # lmd_exp_data = sorted(lmd_exp_data, key=lambda d: d['name'])


class Paths(Enum):
    RESOURCES_PATH: str = pkg_resources.resource_filename(__name__, "resources/resource/")
    OPERATORS_PATH: str = pkg_resources.resource_filename(__name__, "resources/operator/")
    LMD_EXP_PATH: str = pkg_resources.resource_filename(__name__, "resources/explmd.csv")
    LMD_EXP_DATA: list = lmd_exp_data
