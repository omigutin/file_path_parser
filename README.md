# Path Name Parser

Universal, extensible Python library for extracting structured information (groups, dates, times, custom patterns) from file names and paths.

- **No hardcoded logic:** you choose any number of groups (lists, enums, dicts, strings).
- **Automatic date and time search** (many formats supported and validated).
- **Unlimited custom patterns:** add your own regex groups.
- **Configurable priority:** filename or path takes precedence.
- **Supports `str` and `pathlib.Path`.**
- **Returns `None` if not found or not valid.**

---

## Installation

```bash
pip install path_name_parser
```

---


## Supported Date and Time Formats
**Date examples:**
- 20240622           (YYYYMMDD)
- 2024-06-22         (YYYY-MM-DD)
- 2024_06_22         (YYYY_MM_DD)
- 22.06.2024         (DD.MM.YYYY)
- 22-06-2024         (DD-MM-YYYY)
- 220624             (YYMMDD)
- 2024-6-2, 2024_6_2

**Time examples:**
- 154212             (HHMMSS)
- 1542               (HHMM)
- 15-42-12           (HH-MM-SS)
- 15_42_12           (HH_MM_SS)
- 15-42, 15_42       (HH-MM, HH_MM)

All dates and times are validated. E.g. "20241341" is not a date; "246199" is not a time.

---

## Usage Examples

### 1. Lists and Tuples as Groups
```python
from path_name_parser import PathNameParser

animals = ["cat", "dog"]
shifts = ("night", "day")
departments = {"department": ["prod", "dev", "test"]}

parser = PathNameParser(
    animals,
    shifts,
    departments,
    date=True,
    time=True,
    patterns={"cam": r"cam\d{1,2}"}
)

result = parser.parse("cat_night_dev_cam08_20240622_1542.jpg")
print(result)
# {
#   "group1": "cat",
#   "group2": "night",
#   "department": "dev",
#   "date": "20240622",
#   "time": "1542",
#   "cam": "cam08"
# }
```
### 2. Enum as Groups
```python
from path_name_parser import PathNameParser
from enum import Enum

class Shift(Enum):
    NIGHT = "night"
    DAY = "day"

class Animal(Enum):
    CAT = "cat"
    DOG = "dog"

parser = PathNameParser(
    Animal,
    Shift,
    date=True,
    time=True,
    patterns={"cam": r"cam\d{1,2}"}
)

result = parser.parse("dog_day_cam12_2024-06-23_1730.avi")
print(result)
# {
#   "animal": "dog",
#   "shift": "day",
#   "date": "2024-06-23",
#   "time": "1730",
#   "cam": "cam12"
# }
```

### 3. Dictionary as Group
```python
from path_name_parser import PathNameParser

departments = {"department": ["it", "finance", "marketing"]}
levels = {"level": ("junior", "middle", "senior")}
flags = {"flag": "urgent"}

parser = PathNameParser(
    departments,
    levels,
    flags,
    date=True,
    patterns={"ticket": r"T\d{3,5}"}
)

result = parser.parse("finance_senior_urgent_T1004_20240601.txt")
print(result)
# {
#   "department": "finance",
#   "level": "senior",
#   "flag": "urgent",
#   "date": "20240601",
#   "ticket": "T1004"
# }
```

### 4. Mixed Groups: Enum, List, Custom Patterns, Date, and Time
```python
from path_name_parser import PathNameParser
from enum import Enum

class Status(Enum):
    OPEN = "open"
    CLOSED = "closed"

parser = PathNameParser(
    Status,
    ["alpha", "beta"],
    date=True,
    time=True,
    patterns={"session": r"session\d+"}
)

result = parser.parse("beta_open_session27_2023-12-31_2359.txt")
print(result)
# {
#   "status": "open",
#   "group2": "beta",
#   "date": "2023-12-31",
#   "time": "2359",
#   "session": "session27"
# }
```

### 5. Only Custom Patterns and Date/Time
```python
from path_name_parser import PathNameParser

parser = PathNameParser(
    date=True,
    time=True,
    patterns={"id": r"id\d+", "batch": r"batch\d{2,4}"}
)

result = parser.parse("id99_batch012_20240701_1430.log")
print(result)
# {
#   "date": "20240701",
#   "time": "1430",
#   "id": "id99",
#   "batch": "batch012"
# }
```

---

## API Reference
```python
class PathNameParser:
    def __init__(
        *groups: Any,        # Any number of lists, enums, dicts, or strings (group name auto-detected)
        date: bool = False,  # Extract date? (default: False)
        time: bool = False,  # Extract time? (default: False)
        separator: str = "_",
        priority: str = "filename", # or "path"
        patterns: dict = None,      # e.g. {"cam": r"cam\d+"}
    )

    def parse(self, full_path: Union[str, Path]) -> dict:
        """
        Returns a dict {group: value or None, ...}.
        """
```
* **Group name** is auto-generated:
  * Enum: lowercase enum class name.
  * Dict: key as group name.
  * List/tuple/set: groupN (N = order of argument).
  * String: value as group name.
* If group not found or invalid: returns None for that group.
* **Date and time** always validated (returns None if not real date/time).

---

## How It Works
1. Splits filename and path into “blocks” (by `_`, `-`, `.`, `/`, etc).

2. For each group, tries to find an exact match (for enums, lists, dicts).

3. For `date` and `time`:  
   - Matches all supported formats via regex.
   - Validates with `datetime.strptime`.

4. For custom patterns:  
   - Uses provided regex patterns.

If both path and filename have a group, the value from `priority` wins.

---

## Notes
* Group name in the result will be None if not found or not valid.
* If both path and filename have the group, value from priority wins.
* You can use any number of groups or patterns — no hard limit.

---

## Contributing
Pull requests, bug reports and feature requests are welcome!

---

## License
MIT

---
