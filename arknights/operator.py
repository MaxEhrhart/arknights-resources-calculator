# encoding: utf-8
from collections import Counter
from dataclasses import dataclass
from functools import reduce
from pathlib import Path
from typing import Optional, List, Dict
from arknights import constants
from arknights import utils


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

    def __post_init__(self):
        """Load operator info"""
        path = Path(constants.Paths.OPERATORS_PATH.value).resolve()
        operator_path = path.rglob(f'*/{self.name}.json')
        self.json_data = utils.read_json(file_path=str(next(operator_path)), show=False)
        self.stars = self.json_data['stars']

    # TODO
    @property  # Amiya Masteries
    def s4_mastery(self):
        return 0

    # TODO
    @property  # Amiya Masteries
    def s5_mastery(self):
        return 0

    @property
    def elite1_resources(self):
        resources = dict()
        for elite in self.json_data['elite']:
            if elite['level'] == 1:
                for resource in elite['resources']:
                    key, value = resource['name'], resource['quantity']
                    resources[key] = resources.get(key, 0) + value
        return resources

    @property
    def elite2_resources(self):
        resources = dict()
        for elite in self.json_data['elite']:
            if elite['level'] == 2:
                for resource in elite['resources']:
                    key, value = resource['name'], resource['quantity']
                    resources[key] = resources.get(key, 0) + value
        return resources

    @property
    def elite_resources(self):
        return dict(Counter(self.elite1_resources) + Counter(self.elite2_resources))

    @property
    def skill_resources(self):
        upgrades_resources: List[Dict] = list()
        for level in self.json_data['skills']['upgrade']:
            level_resources = dict()
            for resource in level['resources']:
                key, value = resource['name'], resource['quantity']
                level_resources[key] = level_resources.get(key, 0) + value
            upgrades_resources.append(level_resources)
        resources = reduce(lambda x, y: dict(Counter(x) + Counter(y)), upgrades_resources)
        return resources

    @property
    def mastery_resources(self):
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

    @property
    def total_resources(self):
        return dict(Counter(self.skill_resources) + Counter(self.elite_resources) + Counter(self.mastery_resources))

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
                break
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

    # TODO
    @property
    def needed_resources(self):
        return {}

    @property
    def total_lmd(self):
        return {}

    @property
    def spent_lmd(self):
        return {}

    @property
    def needed_lmd(self):
        return {}

    @property
    def total_yellow_exp(self):
        return 0

    @property
    def spent_yellow_exp(self):
        return 0

    @property
    def needed_yellow_exp(self):
        return 0


if __name__ == "__main__":
    operator = Operator(name="Saria", elite_level=2, skill_level=7, s1_mastery=3, s2_mastery=3, s3_mastery=3)
    print(operator.spent_resources)
