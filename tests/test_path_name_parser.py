import sys
from pathlib import Path
# Делаем src импортируемым
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from path_name_parser import PathNameParser


def test_parse_smoke():
    known_projects = ["projectX", "mydata", "reportA"]
    custom_patterns = {
        "cam": r"cam\d{1,3}",
        "count": r"count\d{1,3}"
    }

    parser = PathNameParser(groups={
        "known_projects": known_projects,
        "date": True,
        "time": True
    },
        separator="_",
        patterns=custom_patterns)

    out = parser.parse("/tmp/dir1/reportA_night_cam13_count24_20240619_1236.jpg")
    assert out["known_projects"] == "reportA"
    assert out["cam"] == "cam13"
    assert out["count"] == "count24"
    assert out["date"] == "20240619"
    assert out["time"] == "1236"
