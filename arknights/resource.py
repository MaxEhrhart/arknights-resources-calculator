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
    tier: int = 1
    drop: bool = True
    recipe: list = field(default_factory=list)  # List[Resource]


if __name__ == "__main__":
    orirock = Resource(
        name='Orirock',
        tier=1,
        drop=True
    )
    print(orirock.recipe)
