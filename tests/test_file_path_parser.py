import pytest
from pathlib import Path

from file_path_parser.file_path_parser import FilePathParser


@pytest.mark.parametrize(
    "filename,groups,expected",
    [
        ("cat_night.jpg", [["cat", "dog"], ["night", "day"]], {"group1": "cat", "group2": "night"}),
        ("x_y_z.txt", [["a", "b"]], {"group1": None}),
    ],
)
def test_parse_simple_groups(filename, groups, expected):
    parser = FilePathParser(*groups)
    result = parser.parse(filename)
    for key, val in expected.items():
        assert result[key] == val


def test_parse_with_date_time_and_patterns():
    parser = FilePathParser(
        ["cat", "dog"],
        ["night", "day"],
        date=True,
        time=True,
        patterns={"cam": r"cam\d{1,3}"}
    )
    out = parser.parse("cat_night_cam15_20240619_1236.jpg")
    assert out["group1"] == "cat"
    assert out["group2"] == "night"
    assert out["date"] == "20240619"
    assert out["time"] == "1236"
    assert out["cam"] == "15"


def test_parse_path_priority_filename_vs_path():
    parser = FilePathParser(["aaa", "bbb"], date=True, priority="filename")
    path = Path("/root/bbb_20240622/file_aaa_20240619.jpg")
    result = parser.parse(path)
    assert result["group1"] == "aaa"
    assert result["date"] == "20240619"

    parser2 = FilePathParser(["aaa", "bbb"], date=True, priority="path")
    result2 = parser2.parse(path)
    assert result2["group1"] == "bbb"
    assert result2["date"] == "20240622"


def test_parse_with_dict_group_and_case_insensitivity():
    parser = FilePathParser({"color": ["Red", "Blue"]})
    assert parser.parse("something_blue.txt")["color"] == "Blue"
    assert parser.parse("something_red.txt")["color"] == "Red"


def test_parse_with_enum_and_str_group():
    from enum import Enum

    class Animal(Enum):
        CAT = "cat"
        DOG = "dog"
    parser = FilePathParser(Animal, "uniquevalue")
    out = parser.parse("dog_uniquevalue.png")
    assert out["animal"] == "dog"
    assert out["uniquevalue"] == "uniquevalue"


def test_parse_blocks_and_custom_patterns():
    parser = FilePathParser(patterns={"id": r"id\d+"})
    res = parser.parse("foo_id999.txt")
    assert res["id"] == "999"


def test_parse_returns_none_for_missing_groups():
    parser = FilePathParser(["a", "b"], date=True, time=True)
    result = parser.parse("x_y_z.txt")
    assert result["group1"] is None
    assert result.get("date") is None
    assert result.get("time") is None


def test_parse_raises_on_unknown_priority():
    parser = FilePathParser(["a", "b"], date=True, priority="unknown")
    with pytest.raises(ValueError):
        parser.parse("a_b.txt")
