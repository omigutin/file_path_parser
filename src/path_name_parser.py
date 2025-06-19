__all__ = ['PathNameParser']

from typing import Dict, Any, Union, Optional
from pathlib import Path


class PathNameParser:
    def __init__(
        self,
        *groups_args,
        groups: Optional[Dict[str, Any]] = None,
        separator: str = "_",
        priority: str = "filename"
    ):
        if groups is not None:
            self._groups = {k: self._to_str_list(v) for k, v in groups.items()}
        elif groups_args:
            self._groups = {}
            for idx, group in enumerate(groups_args, start=1):
                self._groups[f"group_{idx}"] = self._to_str_list(group)
        else:
            raise ValueError("Provide at least one enum/list or dict as groups")
        self._separator = separator
        self._priority = priority
        self._validate_no_duplicates()

    def parse(self, full_path: Union[str, Path]) -> dict:
        path = Path(full_path)
        filename = path.name
        dirpath = str(path.parent)

        self._log(f"Parsing filename: {filename}")
        data_from_name = self._parse_blocks(filename)

        self._log(f"Parsing directory path: {dirpath}")
        data_from_path = self._parse_blocks(dirpath)

        if self._priority == "filename":
            merged = {**data_from_path, **data_from_name}
        elif self._priority == "path":
            merged = {**data_from_name, **data_from_path}
        else:
            raise ValueError(f"Unknown priority: {self._priority}")

        self._log(f"Result: {merged}")
        return merged

    def _parse_blocks(self, s: str) -> dict:
        blocks = s.split(self._separator)
        result = {}
        for group_name, group_values in self._groups.items():
            found = None
            for value in group_values:
                for block in blocks:
                    if value and value == block:
                        found = value
                        break
                if found:
                    break
            result[group_name] = found
        return result

    def _validate_no_duplicates(self):
        for k, v in self._groups.items():
            s = list(v)
            if len(s) != len(set(s)):
                raise ValueError(f"Duplicates found in group {k}: {s}")

    @staticmethod
    def _to_str_list(values):
        if hasattr(values, "__members__"):  # Enum class
            return [str(v.value) for v in values]
        if isinstance(values, dict):
            return list(map(str, values.values()))
        return [str(v) for v in values]

    @staticmethod
    def _log(msg):
        print(f"[PathNameParser] {msg}")
