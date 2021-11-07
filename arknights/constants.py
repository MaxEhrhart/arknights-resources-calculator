# encoding: utf-8
import csv
from enum import Enum

import pkg_resources


def load_exp_lmd_data(file):
    with open(pkg_resources.resource_filename(__name__, file), mode="r", encoding="utf-8") as f:
        data = [dict(user_operator) for user_operator in csv.DictReader(f, delimiter=';')]

    for level in data:
        for key, value in level.items():
            level.update({key: int(value)})

    new_data = dict()
    for level in data:
        elite = f"elite_{level['elite']}"
        new_data[elite] = new_data.get(elite, dict())  # Adiciona chave elite_n
        new_data[elite][level['level']] = {
            'exp': level['exp'],
            'lmd': level['lmd'],
            'accumulated exp': level['accumulated exp'],
            'accumulated lmd': level['accumulated lmd']
        }
    return new_data


class Paths(Enum):
    RESOURCES_PATH: str = pkg_resources.resource_filename(__name__, "resources/resource/")
    OPERATORS_PATH: str = pkg_resources.resource_filename(__name__, "resources/operator/")
    EXP_DATA: dict = {i: load_exp_lmd_data(f'resources/explmd/{i}star.csv') for i in range(1, 6 + 1)}
