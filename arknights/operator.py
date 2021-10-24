# encoding: utf-8
from dataclasses import dataclass
from typing import Optional


@dataclass
class Operator:
    # General
    name: str = None
    stars: int = 0
    level: int = 0

    # Elite
    elite_level: int = 0

    # Skill
    skill_level: int = 0

    # Masteries
    s1_mastery: Optional[int] = 0
    s2_mastery: Optional[int] = 0
    s3_mastery: Optional[int] = 0

    # Amiya Masteries
    s4_mastery: Optional[int] = 0
    s5_mastery: Optional[int] = 0


if __name__ == "__main__":
    pass
