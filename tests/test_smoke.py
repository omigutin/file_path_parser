from src.path_name_parser import PathNameParser
from enum import Enum


class Animal(Enum):
    CAT = "cat"
    DOG = "dog"


class Shift(Enum):
    NIGHT = "night"
    DAY = "day"


def test_parse_smoke():
    parser = PathNameParser(groups={"animal": Animal, "shift": Shift}, separator="_")
    out = parser.parse("/tmp/cat/night/testfile_20240619.jpg")
    assert out["animal"] == "cat"
    assert out["shift"] == "night"
