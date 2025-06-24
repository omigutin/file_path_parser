from file_path_parser import parse, create


def test_parse_facade_basic():
    result = parse("cat_night_20240619.txt", ["cat", "dog"], date=True)
    assert result["group1"] == "cat"
    assert result.get("date") == "20240619" or result.get("date") is None


def test_create_parser_facade_basic():
    parser = create(["cat", "dog"], date=True)
    result = parser.parse("dog_night_20240619.txt")
    assert result["group1"] == "dog"
    assert result.get("date") == "20240619" or result.get("date") is None


def test_parse_facade_with_patterns_and_enums():
    from enum import Enum

    class Status(Enum):
        OPEN = "open"
        CLOSED = "closed"
    result = parse(
        "open_beta_cam21_20231231_2359.txt",
        Status, ["beta", "alpha"],
        date=True, time=True, patterns={"cam": r"cam\d{2}"}
    )
    assert result["status"] == "open"
    assert result["group1"] == "beta"
    assert result["date"] == "20231231"
    assert result["time"] == "2359"
    assert result["cam"] == "21"
