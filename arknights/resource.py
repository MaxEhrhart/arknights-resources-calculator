# encoding: utf-8
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

from arknights import constants, utils


def get_resources_data():
    data = []
    for path in Path(constants.Paths.RESOURCES_PATH.value).resolve().glob('*/*.json'):
        data.append(utils.read_json(str(path)))
    return data


@dataclass
class Resource:
    # General
    name: str = None
    tier: int = 0
    drop: bool = True
    recipe: list = field(default_factory=list)  # List[Resource]

    def __post_init__(self):
        """Load resource data."""
        path = Path(constants.Paths.RESOURCES_PATH.value)
        resource_json_path = list(path.rglob(f'*/{self.name}.json'))
        self.json_data = utils.read_json(file_path=str(resource_json_path[0]), show=False)
        self.tier = self.json_data['tier']
        self.drop = self.json_data['droppable']
        self.recipe = self.json_data['recipe']
        self.lmd_cost = self.json_data['lmd']
        print(self.json_data)


if __name__ == "__main__":
    orirock = Resource(name='Aketon')
    print(orirock)
