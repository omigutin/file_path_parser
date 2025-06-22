
# ![Python](https://img.icons8.com/color/32/python.png) FilePathParser

Universal, extensible Python library for extracting structured information (groups, dates, times, custom patterns) from file names and paths.

* **No hardcoded logic:** you choose any number of groups (lists, enums, dicts, strings).
* **Automatic date and time search** (many formats supported and validated).
* **Unlimited custom patterns:** add your own regex groups.
* **Configurable priority:** filename or path takes precedence.
* **Supports `str` and `pathlib.Path`.**
* **Returns `None` if not found or not valid.**
* **Simple interface:** Use just two functions — `parse()` and `create_parser()`.

---

# Table of Contents

* [Installation](#installation)
* [Supported Date and Time Formats](#supported-date-and-time-formats)
* [Usage Examples](#usage-examples)
* [API Reference](#api-reference)
* [How It Works](#how-it-works)
* [Notes](#notes)
* [Command-Line Interface (CLI)](#command-line-interface-cli-for-filepathparser)
* [Contributing](#contributing)
* [Project Board](#project-board)
* [FAQ / Known Issues](#faq--known-issues)
* [Author](#author)
* [License](#license)

---

## Installation

```bash
pip install file_path_parser
```

---

## Supported Date and Time Formats

**Date examples:**
* 20240622           (YYYYMMDD)
* 2024-06-22         (YYYY-MM-DD)
* 2024_06_22         (YYYY_MM_DD)
* 22.06.2024         (DD.MM.YYYY)
* 22-06-2024         (DD-MM-YYYY)
* 220624             (YYMMDD)
* 2024-6-2, 2024_6_2

**Time examples:**
* 154212             (HHMMSS)
* 1542               (HHMM)
* 15-42-12           (HH-MM-SS)
* 15_42_12           (HH_MM_SS)
* 15-42, 15_42       (HH-MM, HH_MM)

All dates and times are validated. E.g. "20241341" is not a date; "246199" is not a time.

---

## Usage Examples

All parsing is done through the **interface functions** — use only these for a clean API:

### 1. Quick one-line parsing (main use case)

```python
from file_path_parser.api import parse

result = parse(
    "cat_night_cam15_20240619_1236.jpg",
    ["cat", "dog"], ["night", "day"],
    date=True, time=True, patterns={"cam": r"cam\d{1,3}"}
)
print(result)
# {'group1': 'cat', 'group2': 'night', 'date': '20240619', 'time': '1236', 'cam': '15'}
```

### 2. Create a reusable parser

```python
from file_path_parser.api import create_parser

parser = create_parser(
    ["cat", "dog"], ["night", "day"],
    date=True, time=True, patterns={"cam": r"cam\d{1,3}"}
)
result = parser.parse("dog_night_cam22_20240620_0815.jpg")
print(result)
# {'group1': 'dog', 'group2': 'night', 'date': '20240620', 'time': '0815', 'cam': '22'}
```

### More usage: Dicts, Enums, Priority, etc.

```python
from enum import Enum
from file_path_parser.api import parse

class Status(Enum):
    OPEN = "open"
    CLOSED = "closed"

result = parse(
    "open_beta_cam21_20231231_2359.txt",
    Status, ["beta", "alpha"],
    date=True, time=True, patterns={"cam": r"cam\d{2}"}
)
print(result)
# {'status': 'open', 'group1': 'beta', 'date': '20231231', 'time': '2359', 'cam': '21'}
```

#### If both the path and filename contain a group, the `priority` parameter wins.

```python
from file_path_parser.api import parse

result = parse(
    "/data/prod/archive/test_20240620.csv",
    ["prod", "test"], date=True, priority="filename"
)
print(result)
# If priority="filename", group1 == "test"
# If priority="path", group1 == "prod"
```

---

## API Reference

```python
from file_path_parser.api import parse, create_parser

def parse(full_path: str, *groups, date=False, time=False, separator="_", priority="filename", patterns=None) -> dict:
    '''
    One-line parsing.
    '''

def create_parser(*groups, date=False, time=False, separator="_", priority="filename", patterns=None) -> FilePathParser:
    '''
    Returns a reusable parser object.
    '''
```

* **Group name** is auto-generated:
  * Enum: lowercase enum class name.
  * Dict: key as group name.
  * List/tuple/set: groupN (N = order of argument).
  * String: value as group name.
* If group not found or invalid: returns None for that group.
* **Date and time** always validated (returns None if not real date/time).
* **Custom patterns**: returns only the captured number (not the full match, e.g. `cam15` → `15`).

---

## How It Works

1. Splits filename and path into “blocks” (by `_`, `-`, `.`, `/`, etc).
2. For each group, tries to find an exact match (for enums, lists, dicts).
3. For `date` and `time`:
   * Matches all supported formats via regex.
   * Validates with `datetime.strptime`.
4. For custom patterns:
   * Uses provided regex patterns.
   * **Returns only the matched number** (if the pattern looks like `cam\d+`, the result is `'15'` for `cam15`).  
     If you want the full match, add explicit parentheses: `patterns={"cam": r"(cam\d+)"}`

If both path and filename have a group, the value from `priority` wins.

---

## Notes

* Group name in the result will be None if not found or not valid.
* If both path and filename have the group, value from priority wins.
* You can use any number of groups or patterns — no hard limit.
* **PatternMatcher.find_special:**  
  This internal method is not used by default, but can be handy for advanced scenarios (e.g., direct pattern lookup in a string, testing, or future extensions).

---

# Command-Line Interface (CLI) for FilePathParser

The library supports a convenient command-line interface (CLI) for extracting structured information from file names and paths.

---

## 🚀 Quick Start

After installing dependencies with Poetry, you can use the `file-path-parser` utility to parse file names directly from your terminal.

### Example usage

```bash
poetry run file-path-parser "cat_night_cam15_20240619_1236.jpg" --groups cat dog --classes night day --date --time --pattern cam "cam\d{1,3}"
```

### Show help

```bash
poetry run file-path-parser --help
```

---

## CLI Options

* `filepath` — Path or file name to parse
* `--groups` — List of allowed groups (e.g. `cat dog`)
* `--classes` — List of allowed classes (e.g. `night day`)
* `--date` — Enable date parsing
* `--time` — Enable time parsing
* `--pattern NAME REGEX` — Add custom pattern (can be used multiple times)

---

### Example

```bash
poetry run file-path-parser "dog_day_cam2_20240701_0800.jpg" --groups cat dog --classes night day --date --time --pattern cam "cam\d{1,3}"
```

The parsing result will be displayed in the terminal.

---

## Contributing

Pull requests, bug reports and feature requests are welcome!

---

## Project Board

All ongoing development, task tracking, and planning for this library is managed in the [Project Board](https://github.com/users/omigutin/projects/1).

- **See what's in progress, planned, or completed**
- **Follow the roadmap and feature development**
- **Suggest improvements or report issues via Issues, which are linked directly to the board**

> [Visit the Project Board →](https://github.com/users/omigutin/projects/1)

---

## FAQ / Known Issues

### Q: What happens if both the path and filename contain the same group, but with different values?

**A:** The result depends on the `priority` parameter:

* If `priority="filename"` (default), the group value from the filename wins.
* If `priority="path"`, the value from the directory path wins.

### Q: Can I use non-Latin or Unicode characters in group values?

**A:** Yes. Groups and blocks are matched in a case-insensitive way and support Unicode.

### Q: What separators does the parser recognize between blocks?

**A:** By default, the parser splits by any of these: `_`, `-`, `.`, `/`, `\`, `{}`, or space.
If your files use custom separators, let us know!

### Q: What if a value looks like a date/time, but is not real?

**A:** The parser validates all dates/times. "20241341" (wrong month/day) will not be recognized as a date, etc.

### Q: What will be returned for custom patterns?

**A:**  
* If you use e.g. `patterns={"cam": r"cam\d+"}`, you get just the number, e.g. `'cam15'` → `'15'`.  
* If you want the full match (e.g. `'cam15'`), use explicit parentheses: `patterns={"cam": r"(cam\d+)"}`.

### Known Issues

* If your separator is unusual (not in the list above), you may need to pre-process filenames.
* Extremely exotic date/time formats (not listed in "Supported formats") are not matched.
* Path parsing supports both `str` and `pathlib.Path`, but network/multiplatform paths (e.g., UNC, SMB) are not specifically tested.

---

## Author

[![Telegram](https://img.shields.io/badge/-Telegram-26A5E4?style=flat&logo=telegram&logoColor=white)](https://t.me/omigutin)
[![GitHub](https://img.shields.io/badge/-GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/omigutin)

---

## License

MIT
