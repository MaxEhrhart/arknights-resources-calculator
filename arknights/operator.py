# encoding: utf-8
import csv
from collections import Counter
from dataclasses import dataclass
from functools import reduce
from pathlib import Path
from typing import Optional, List, Dict

from arknights import constants
from arknights import utils


def get_operators_data():
    data = []
    for path in Path(constants.Paths.OPERATORS_PATH.value).resolve().glob('*/*.json'):
        data.append(utils.read_json(str(path)))
    return data


def instantiate_operator(operator_dict: dict):
    return Operator(
        name=operator_dict.get('name', None),
        elite_level=int(operator_dict.get('elite', 0)),
        skill_level=int(operator_dict.get('skill_level', 0)),
        s1_mastery=int(operator_dict.get('s1_mastery', 0)),
        s2_mastery=int(operator_dict.get('s2_mastery', 0)),
        s3_mastery=int(operator_dict.get('s3_mastery', 0)),
        s4_mastery=int(operator_dict.get('s4_mastery', 0)),
        s5_mastery=int(operator_dict.get('s5_mastery', 0))
    )


def load_operators(csv_path: str):
    with open(csv_path, mode="r", encoding="utf-8") as f:
        operators_data = [dict(user_operator) for user_operator in csv.DictReader(f, delimiter=';')]
    operators = [instantiate_operator(operator_data) for operator_data in operators_data]
    return operators


@dataclass
class Operator:
    name: str = None  # General
    level: int = 0  # General
    stars: Optional[int] = 0  # General
    elite_level: int = 0  # Elite
    skill_level: int = 0  # Skill
    s1_mastery: Optional[int] = 0  # Masteries
    s2_mastery: Optional[int] = 0  # Masteries
    s3_mastery: Optional[int] = 0  # Masteries
    s4_mastery: Optional[int] = 0  # Amiya Masteries
    s5_mastery: Optional[int] = 0  # Amiya Masteries

    def __post_init__(self):
        """Load operator info"""
        path = Path(constants.Paths.OPERATORS_PATH.value)
        operator_json_path = list(path.rglob(f'*/{self.name}.json'))
        self.json_data = utils.read_json(file_path=str(operator_json_path[0]), show=False)
        self.stars = self.json_data['stars']

    # Elite
    @property
    def total_elite_resources(self):
        resources = dict()
        for elite in self.json_data['elite']:
            for resource in elite['resources']:
                key, value = resource['name'], resource['quantity']
                resources[key] = resources.get(key, 0) + value
        return resources

    # Skill
    @property
    def total_skill_resources(self):
        upgrades_resources: List[Dict] = list()
        for level in self.json_data['skills']['upgrade']:
            level_resources = dict()
            for resource in level['resources']:
                key, value = resource['name'], resource['quantity']
                level_resources[key] = level_resources.get(key, 0) + value
            upgrades_resources.append(level_resources)
        resources = reduce(lambda x, y: dict(Counter(x) + Counter(y)), upgrades_resources)
        return resources

    # Mastery
    @property
    def total_mastery_resources(self):
        if self.stars <= 3:
            return {}
        mastery_resources: List[Dict] = list()
        for mastery in self.json_data['skills']['mastery']:
            for level in mastery['upgrade']:
                level_resources = dict()
                for resource in level['resources']:
                    key, value = resource['name'], resource['quantity']
                    level_resources[key] = level_resources.get(key, 0) + value
                mastery_resources.append(level_resources)
        resources = reduce(lambda x, y: dict(Counter(x) + Counter(y)), mastery_resources)
        return resources

    # Total
    @property
    def total_resources(self):
        total = dict()
        total = Counter(total) + Counter(self.total_skill_resources)
        total = Counter(total) + Counter(self.total_elite_resources)
        total = Counter(total) + Counter(self.total_mastery_resources)
        return dict(total)

    # region Spent
    @property
    def spent_elite_resources(self):
        resources = dict()
        for elite in self.json_data['elite']:
            if self.elite_level < elite['level']:
                break
            for resource in elite['resources']:
                key = resource['name']
                value = resource['quantity']
                resources[key] = resources.get(key, 0) + value
        return resources

    @property
    def spent_skill_resources(self):
        resources = dict()
        for skill in self.json_data['skills']['upgrade']:
            if self.skill_level < skill['level']:
                break
            for resource in skill['resources']:
                key = resource['name']
                value = resource['quantity']
                resources[key] = resources.get(key, 0) + value
        return resources

    @property
    def spent_mastery_resources(self):
        operator_masteries = {
            's1_mastery': self.s1_mastery,
            's2_mastery': self.s2_mastery,
            's3_mastery': self.s3_mastery,
            's4_mastery': self.s4_mastery,
            's5_mastery': self.s5_mastery
        }
        resources = dict()
        for mastery in self.json_data['skills']['mastery']:
            skill_mastery = int(operator_masteries[f's{mastery["skill"]}_mastery'])
            if skill_mastery <= 0:
                continue
            for level in mastery['upgrade']:
                if level['level'] > skill_mastery:
                    break
                for resource in level['resources']:
                    key = resource['name']
                    value = resource['quantity']
                    resources[key] = resources.get(key, 0) + value
        return resources

    @property
    def spent_resources(self):
        total = dict()
        total = Counter(total) + Counter(self.spent_skill_resources)
        total = Counter(total) + Counter(self.spent_elite_resources)
        total = Counter(total) + Counter(self.spent_mastery_resources)
        return dict(total)

    # endregion

    # region Needed
    @property
    def needed_elite_resources(self):
        resources = Counter(self.total_elite_resources) - Counter(self.spent_elite_resources)
        return dict(resources)

    @property
    def needed_skill_resources(self):
        resources = Counter(self.total_skill_resources) - Counter(self.spent_skill_resources)
        return dict(resources)

    @property
    def needed_mastery_resources(self):
        resources = Counter(self.total_mastery_resources) - Counter(self.spent_mastery_resources)
        return dict(resources)

    @property
    def needed_resources(self):
        return dict(Counter(self.total_resources) - Counter(self.spent_resources))

    # endregion

    # Quantities
    @property
    def total_material_quantity(self):
        total_resources = self.total_resources
        total_resources.pop('LMD', None)
        return sum(total_resources.values())

    @property
    def spent_material_quantity(self):
        spent_resources = self.spent_resources
        spent_resources.pop('LMD', None)
        return sum(spent_resources.values())

    @property
    def needed_material_quantity(self):
        needed_resources = self.needed_resources
        needed_resources.pop('LMD', None)
        return sum(needed_resources.values())

    @property
    def material_percentage(self):
        return round((self.spent_material_quantity / self.total_material_quantity) * 100, 2)

    # LMD
    # TODO
    @property
    def total_lmd(self):
        return {}

    # TODO
    @property
    def spent_lmd(self):
        return {}

    # TODO
    @property
    def needed_lmd(self):
        return {}

    # EXP
    # TODO
    @property
    def total_yellow_exp(self):
        return 0

    # TODO
    @property
    def spent_yellow_exp(self):
        return 0

    # TODO
    @property
    def needed_yellow_exp(self):
        return 0

    def to_dict(self):
        attributes = {
            # General
            'name': self.name,
            'stars': self.stars,
            'elite': self.elite_level,
            # Skills
            'skill_level': self.skill_level,
            # Masteries
            's1_mastery': self.s1_mastery,
            's2_mastery': self.s2_mastery,
            's3_mastery': self.s3_mastery,
            # Resources
            'skill_upgrade_resources': self.total_skill_resources,
            'elite_resources': self.total_elite_resources,
            'mastery_resources': self.total_mastery_resources,
            'total_resources': self.total_resources,
            'spent_resources': self.spent_resources,
            'needed_resources': self.needed_resources,
            # Quantities
            'total_material_quantity': self.total_material_quantity,
            'spent_material_quantity': self.spent_material_quantity,
            'needed_material_quantity': self.needed_material_quantity,
            # Needed
            'needed_elite_resources': self.needed_elite_resources,
            'needed_mastery_resources': self.needed_mastery_resources,
            'needed_skill_resources': self.needed_skill_resources,
            # Percentage
            'material_percentage': self.material_percentage
        }
        return attributes


if __name__ == "__main__":
    operator = Operator(name="Aak", elite_level=1, skill_level=7, s1_mastery=0, s2_mastery=0, s3_mastery=0)
    print(operator.spent_resources)
    print(operator.needed_resources)
    print(operator.total_resources)
    print(operator.total_material_quantity)
    print(operator.spent_material_quantity)
    print(operator.needed_material_quantity)
