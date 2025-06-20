import pytest

from file_path_parser.file_path_parser import PatternMatcher


def test_is_valid_date_all_formats():
    matcher = PatternMatcher()
    assert matcher.is_valid_date("20240622")
    assert matcher.is_valid_date("2024-06-22")
    assert matcher.is_valid_date("2024_06_22")
    assert matcher.is_valid_date("22.06.2024")
    assert matcher.is_valid_date("22-06-2024")
    assert matcher.is_valid_date("240622")
    assert not matcher.is_valid_date("notadate")


def test_is_valid_time_all_formats():
    matcher = PatternMatcher()
    assert matcher.is_valid_time("154212")
    assert matcher.is_valid_time("1542")
    assert matcher.is_valid_time("15-42-12")
    assert matcher.is_valid_time("15_42_12")
    assert matcher.is_valid_time("15-42")
    assert matcher.is_valid_time("15_42")
    assert not matcher.is_valid_time("256789")
    assert not matcher.is_valid_time("hello")


def test_find_by_patterns_returns_first_match():
    matcher = PatternMatcher()
    assert matcher.find_by_patterns("foo20240622bar", [r"\d{8}"]) == "20240622"
    assert matcher.find_by_patterns("foo", [r"\d+"]) is None


def test_find_special_date_time_custom():
    matcher = PatternMatcher(user_patterns={"cam": r"cam\d{1,2}"})
    assert matcher.find_special("abc20240622", "date") == "20240622"
    assert matcher.find_special("foo1542bar", "time") == "1542"
    assert matcher.find_special("cam12_x", "cam") == "cam12"
    assert matcher.find_special("zzz", "cam") is None
    assert matcher.find_special("abc", "unknown") is None
