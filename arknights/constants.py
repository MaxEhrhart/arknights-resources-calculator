# encoding: utf-8
from dataclasses import dataclass
from enum import Enum
import pkg_resources


class Paths(Enum):
    RESOURCES_PATH: str = pkg_resources.resource_filename(__name__, "resources/resource/")
    OPERATORS_PATH: str = pkg_resources.resource_filename(__name__, "resources/operator/")
    LMD_EXP_PATH: str = pkg_resources.resource_filename(__name__, "resources/explmd.csv")

    def __repr__(self):
        return self.value

    def __str__(self):
        return self.value
