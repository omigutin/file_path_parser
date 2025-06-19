# PathNameParser

**PathNameParser** is a flexible and universal Python library for extracting structured keywords (groups) from both filenames and directory paths.

- Works for any files: images, videos, documents, datasets, and more.
- Supports any number of groups (category, type, region, shift, etc.), provided as enums, lists, or dictionaries.
- Customizable separator for splitting names into blocks (default: `_`).
- Smart priority: extract values from filename, path, or combine both.
- No external dependencies.

## Features

- ⚡️ Parse any number of groups from any file or directory name.
- 🛠️ Accepts enums, lists, or dicts as group sources.
- 🔧 Customizable block separator (default: `_`).
- 🎯 Priority option: `"filename"` or `"path"`.
- ✅ Checks for duplicate values inside groups.
- 🔗 Supports both `str` and `pathlib.Path`.

## Installation

**With Poetry:**
```bash
poetry add path_name_parser
```

## Usage

```python
from src.path_name_parser import PathNameParser
from enum import Enum

class Animal(Enum):
    CAT = "cat"
    DOG = "dog"

class Shift(Enum):
    NIGHT = "night"
    DAY = "day"

# Example 1: Using a dict for named groups
parser = PathNameParser(groups={"animal": Animal, "shift": Shift}, separator="_")
result = parser.parse("dog_night_20240619.jpg")
print(result)
# {'animal': 'dog', 'shift': 'night'}

# Example 2: Passing several enums/lists directly (auto-named: group_1, group_2, ...)
parser2 = PathNameParser(Animal, Shift, separator="_")
result2 = parser2.parse("cat_day_20240619.jpg")
print(result2)
# {'group_1': 'cat', 'group_2': 'day'}

# Example 3: Parsing path with priority
parser3 = PathNameParser(groups={"animal": Animal, "shift": Shift}, separator="_", priority="path")
result3 = parser3.parse("/images/dog/night/20240619.jpg")
print(result3)
# {'animal': 'dog', 'shift': 'night'}
```

## API
PathNameParser(*groups_args, groups=None, separator='_', priority='filename')
* groups_args: any number of enums or lists (will be named group_1, group_2, ...).
* groups: dict of group_name → enum/list.
* separator: character(s) for splitting names into blocks.
* priority: "filename" (default) or "path".

`.parse(path: str | Path) → dict`

Returns a dictionary:
`{group_name: found_value or None, ...}`

Testing
To run tests:
```bash
pytest tests
```

## License
MIT
