# encoding: utf-8
from __future__ import annotations
from dataclasses import dataclass, field


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
