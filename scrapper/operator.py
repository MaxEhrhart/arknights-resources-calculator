from dataclasses import dataclass
from typing import Optional, List
import json


@dataclass
class Resource:
    name: str
    quantity: int

    @staticmethod
    def is_filled(var):
        return var is not None

    def validate(self):
        if not self.is_filled(self.name):
            return

    def load(self, data: dict) -> None:
        self.name = data.get('name')
        self.quantity = data.get('quantity')

    def __init__(self, data):
        if data is not None:
            self.load(data)
            self.validate()

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)


@dataclass
class Upgrade:
    level: int
    resources: List[Resource]

    @staticmethod
    def is_filled(var):
        return var is not None

    def validate(self):
        if not self.is_filled(self.level):
            return

    def load(self, data: dict) -> None:
        self.level = data.get('level')
        self.resources = [Resource(resource) for resource in data.get('resources', None)]

    def to_dict(self):
        result = dict()
        if self.resources is not None:
            result['resources'] = [resource.__dict__ for resource in self.resources]
        return result

    def __init__(self, data):
        if data is not None:
            self.load(data)
            self.validate()

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)


@dataclass
class Skills:
    upgrade: List[Upgrade]

    @staticmethod
    def is_filled(var):
        return var is not None

    def validate(self):
        if not self.is_filled(self.upgrade):
            return

    def load(self, data: dict) -> None:
        self.upgrade = [Upgrade(upgrade) for upgrade in data.get('upgrade', None)]

    def to_dict(self):
        result = dict()
        if self.upgrade is not None:
            result['upgrade'] = [upgrade.__dict__ for upgrade in self.upgrade]
        return result

    def __init__(self, data):
        if data is not None:
            self.load(data)
            self.validate()

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)


@dataclass
class Operator:
    name: str
    stars: int
    skills: Optional[Skills] = None

    @staticmethod
    def is_filled(var):
        return var is not None

    def validate(self):
        if not self.is_filled(self.name):
            return

    def load(self, data: dict) -> None:
        self.name = data.get('name')
        self.stars = data.get('stars', 0)
        self.skills = Skills(data.get('skills', None))

    def __init__(self, data):
        if data is not None:
            self.load(data)
            self.validate()

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)


x = {
    "name": "Fiammetta",
    "stars": 6,
    "skills": {
        "upgrade": [
            {
                "level": 1,
                "resources": [

                ]
            },
            {
                "level": 2,
                "resources": [
                    {
                        "name": "Skill Summary - 1",
                        "quantity": 5
                    }
                ]
            },
            {
                "level": 3,
                "resources": [
                    {
                        "name": "Skill Summary - 1",
                        "quantity": 5
                    },
                    {
                        "name": "Orirock",
                        "quantity": 6
                    },
                    {
                        "name": "Damaged Device",
                        "quantity": 4
                    }
                ]
            },
            {
                "level": 4,
                "resources": [
                    {
                        "name": "Skill Summary - 2",
                        "quantity": 8
                    },
                    {
                        "name": "Sugar",
                        "quantity": 5
                    }
                ]
            },
            {
                "level": 5,
                "resources": [
                    {
                        "name": "Skill Summary - 2",
                        "quantity": 8
                    },
                    {
                        "name": "Polyester",
                        "quantity": 4
                    },
                    {
                        "name": "Oriron",
                        "quantity": 4
                    }
                ]
            },
            {
                "level": 6,
                "resources": [
                    {
                        "name": "Skill Summary - 2",
                        "quantity": 8
                    },
                    {
                        "name": "Coagulating Gel",
                        "quantity": 5
                    }
                ]
            },
            {
                "level": 7,
                "resources": [
                    {
                        "name": "Skill Summary - 3",
                        "quantity": 8
                    },
                    {
                        "name": "Incandescent Alloy",
                        "quantity": 4
                    },
                    {
                        "name": "Manganese Ore",
                        "quantity": 5
                    }
                ]
            }
        ],
        "mastery": [
            {
                "skill": 1,
                "upgrade": [
                    {
                        "level": 1,
                        "resources": [
                            {
                                "name": "Skill Summary - 3",
                                "quantity": 8
                            },
                            {
                                "name": "Grindstone Pentahydrate",
                                "quantity": 4
                            },
                            {
                                "name": "Loxic Kohl",
                                "quantity": 7
                            }
                        ]
                    },
                    {
                        "level": 2,
                        "resources": [
                            {
                                "name": "Skill Summary - 3",
                                "quantity": 12
                            },
                            {
                                "name": "Keton Colloid",
                                "quantity": 4
                            },
                            {
                                "name": "Cutting Stock Solution",
                                "quantity": 8
                            }
                        ]
                    },
                    {
                        "level": 3,
                        "resources": [
                            {
                                "name": "Skill Summary - 3",
                                "quantity": 15
                            },
                            {
                                "name": "Crystalline Electroassembly",
                                "quantity": 6
                            },
                            {
                                "name": "Grindstone Pentahydrate",
                                "quantity": 4
                            }
                        ]
                    }
                ]
            },
            {
                "skill": 2,
                "upgrade": [
                    {
                        "level": 1,
                        "resources": [
                            {
                                "name": "Skill Summary - 3",
                                "quantity": 8
                            },
                            {
                                "name": "RMA70-24",
                                "quantity": 3
                            },
                            {
                                "name": "Manganese Ore",
                                "quantity": 9
                            }
                        ]
                    },
                    {
                        "level": 2,
                        "resources": [
                            {
                                "name": "Skill Summary - 3",
                                "quantity": 12
                            },
                            {
                                "name": "Optimized Device",
                                "quantity": 3
                            },
                            {
                                "name": "Oriron Block",
                                "quantity": 6
                            }
                        ]
                    },
                    {
                        "level": 3,
                        "resources": [
                            {
                                "name": "Skill Summary - 3",
                                "quantity": 15
                            },
                            {
                                "name": "Bipolar Nanoflake",
                                "quantity": 6
                            },
                            {
                                "name": "White Horse Kohl",
                                "quantity": 5
                            }
                        ]
                    }
                ]
            },
            {
                "skill": 3,
                "upgrade": [
                    {
                        "level": 1,
                        "resources": [
                            {
                                "name": "Skill Summary - 3",
                                "quantity": 8
                            },
                            {
                                "name": "Crystalline Circuit",
                                "quantity": 4
                            },
                            {
                                "name": "Coagulating Gel",
                                "quantity": 3
                            }
                        ]
                    },
                    {
                        "level": 2,
                        "resources": [
                            {
                                "name": "Skill Summary - 3",
                                "quantity": 12
                            },
                            {
                                "name": "White Horse Kohl",
                                "quantity": 4
                            },
                            {
                                "name": "Keton Colloid",
                                "quantity": 8
                            }
                        ]
                    },
                    {
                        "level": 3,
                        "resources": [
                            {
                                "name": "Skill Summary - 3",
                                "quantity": 15
                            },
                            {
                                "name": "Polymerization Preparation",
                                "quantity": 6
                            },
                            {
                                "name": "Manganese Trihydrate",
                                "quantity": 7
                            }
                        ]
                    }
                ]
            }
        ]
    },
    "elite": [
        {
            "level": 1,
            "resources": [
                {
                    "name": "LMD",
                    "quantity": 30000
                },
                {
                    "name": "Sniper Chip",
                    "quantity": 5
                },
                {
                    "name": "Device",
                    "quantity": 6
                },
                {
                    "name": "Sugar",
                    "quantity": 4
                }
            ]
        },
        {
            "level": 2,
            "resources": [
                {
                    "name": "LMD",
                    "quantity": 180000
                },
                {
                    "name": "Sniper Dualchip",
                    "quantity": 4
                },
                {
                    "name": "Crystalline Electroassembly",
                    "quantity": 3
                },
                {
                    "name": "Grindstone Pentahydrate",
                    "quantity": 6
                }
            ]
        }
    ]
}


if __name__ == "__main__":
    operator = Operator(x)
    print(operator)
