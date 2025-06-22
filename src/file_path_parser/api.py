__all__ = ['parse', 'create_parser']

from pathlib import Path
from typing import Any, Dict, Optional, Union

from .file_path_parser import FilePathParser


def parse(
    full_path: Union[str, Path],
    *groups: Any,
    date: bool = False,
    time: bool = False,
    separator: str = "_",
    priority: str = "filename",
    patterns: Optional[Dict[str, str]] = None,
) -> Dict[str, Optional[str]]:
    """
        Facade function for quick, one-line parsing of file paths/names.
        Initializes FilePathParser with given groups and options, parses the path, and returns the result.
        Example:
            result = parse(
                "cat_night_cam15_20240619_1236.jpg",
                ["cat", "dog"], ["night", "day"],
                date=True, time=True,
                patterns={"cam": r"cam\\d{1,3}"}
            )
        Args:
            full_path: Path or filename to parse (str or Path).
            *groups: Any number of group specs (list/tuple, enum, dict, str).
            date: Extract date? (default: False)
            time: Extract time? (default: False)
            separator: Block separator (default: "_")
            priority: 'filename' or 'path' (default: "filename")
            patterns: Custom regex patterns (e.g. {"cam": r"cam\\d+"})
        Returns:
            Dict with found groups, date, time, custom keys (value is None if not found).
    """
    parser = FilePathParser(
        *groups,
        date=date,
        time=time,
        separator=separator,
        priority=priority,
        patterns=patterns,
    )
    return parser.parse(full_path)


def create_parser(
    *groups: Any,
    date: bool = False,
    time: bool = False,
    separator: str = "_",
    priority: str = "filename",
    patterns: Optional[Dict[str, str]] = None,
) -> Any:
    """
        Factory function for getting a ready-to-use parser object.
        Returns a FilePathParser instance with the specified configuration.
        Example:
            parser = create_parser(["cat", "dog"], date=True)
            result = parser.parse("cat_night_20240619.txt")
        Args:
            *groups: Any number of group specs (list/tuple, enum, dict, str).
            date: Extract date? (default: False)
            time: Extract time? (default: False)
            separator: Block separator (default: "_")
            priority: 'filename' or 'path' (default: "filename")
            patterns: Custom regex patterns (e.g. {"cam": r"cam\\d+"})
        Returns:
            FilePathParser instance (hidden implementation).
    """
    return FilePathParser(
        *groups,
        date=date,
        time=time,
        separator=separator,
        priority=priority,
        patterns=patterns,
    )
