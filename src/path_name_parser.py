__all__ = ['PathNameParser']

import re
from typing import Any, Dict, List, Optional, Union

from pathlib import Path

from pattern_matcher import PatternMatcher


class PathNameParser:
    """
        Универсальный парсер для извлечения групп, дат, времени и кастомных шаблонов
        из имени файла или пути.

        Пример:
            parser = PathNameParser(
                ["cat", "dog"],
                ["night", "day"],
                date=True,
                time=True,
                patterns={"cam": r"cam\d{1,3}"}
            )
            out = parser.parse("cat_night_cam15_20240619_1236.jpg")
            # out == {"group1": "cat", "group2": "night", "date": "20240619", "time": "1236", "cam": "cam15"}
    """

    _groups: Dict[str, List[str]]
    _date: bool
    _time: bool
    _separator: str
    _priority: str
    matcher: PatternMatcher

    def __init__(
        self,
        *groups: Any,
        date: bool = False,
        time: bool = False,
        separator: str = "_",
        priority: str = "filename",
        patterns: Optional[Dict[str, str]] = None,
    ) -> None:
        """
            Args:
                *groups: любое количество списков, Enum, dict, str (имя группы берётся автоматически)
                date: искать дату? (default: False)
                time: искать время? (default: False)
                separator: разделитель блоков (default: "_")
                priority: 'filename' или 'path' (default: "filename")
                patterns: кастомные паттерны (например, {"cam": r"cam\d+"})
        """
        self._groups = self._parse_groups(*groups)
        self._date = date
        self._time = time
        self._separator = separator
        self._priority = priority
        self.matcher = PatternMatcher(patterns)

    @staticmethod
    def _parse_groups(*groups: Any) -> Dict[str, List[str]]:
        """
            Преобразует все пришедшие группы в словарь {group_name: [values]}.

            Args:
                *groups: любые списки, enum, dict, str

            Returns:
                dict: {group_name: [values]}
        """
        result: Dict[str, List[str]] = {}
        group_counter = 1
        for g in groups:
            if hasattr(g, "__members__"):  # Enum
                name = g.__name__.lower()
                result[name] = [str(v.value) for v in g]
            elif isinstance(g, dict):
                for k, v in g.items():
                    name = str(k).lower()
                    values = v if isinstance(v, (list, tuple, set)) else [v]
                    result[name] = [str(val) for val in values]
            elif isinstance(g, (list, tuple, set)):
                name = f"group{group_counter}"
                result[name] = [str(val) for val in g]
                group_counter += 1
            elif isinstance(g, str):
                name = g.lower()
                result[name] = [g]
            else:
                name = g.__class__.__name__.lower()
                result[name] = [str(g)]
        return result

    def parse(self, full_path: Union[str, Path]) -> Dict[str, Optional[str]]:
        """
            Анализирует путь или имя файла, возвращает словарь найденных групп.

            Args:
                full_path: строка или Path до файла/директории

            Returns:
                dict: {group_name: str or None, "date": str or None, "time": str or None, ...}
        """
        path = Path(full_path)
        filename = path.name
        dirpath = str(path.parent)
        data_from_name = self._parse_blocks(filename)
        data_from_path = self._parse_blocks(dirpath)

        if self._priority == "filename":
            merged = {**data_from_path, **data_from_name}
        elif self._priority == "path":
            merged = {**data_from_name, **data_from_path}
        else:
            raise ValueError(f"Unknown priority: {self._priority}")

        return merged

    def _parse_blocks(self, s: str) -> Dict[str, Optional[str]]:
        """
            Разбивает строку по разделителям и извлекает группы, дату, время и кастомные паттерны.

            Args:
                s: строка (файл или путь)

            Returns:
                dict: {group_name: value, ...}
        """
        blocks = [b for b in re.split(r'[\\/{}\-_. ]+', s) if b]
        result: Dict[str, Optional[str]] = {}

        # Группы
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

        # Дата
        date_val = None
        if self._date:
            for b in blocks:
                for pat in self.matcher.DATE_PATTERNS:
                    m = re.fullmatch(pat, b)
                    if m and self.matcher.is_valid_date(m.group(0)):
                        date_val = m.group(0)
                        break
                if date_val:
                    break
            result["date"] = date_val

        # Время
        time_val = None
        if self._time:
            for b in blocks:
                if b == date_val:
                    continue
                for pat in self.matcher.TIME_PATTERNS:
                    m = re.fullmatch(pat, b)
                    if m and self.matcher.is_valid_time(m.group(0)):
                        time_val = m.group(0)
                        break
                if time_val:
                    break
            result["time"] = time_val

        # Кастомные patterns
        if self.matcher.user_patterns:
            for group_name, pat in self.matcher.user_patterns.items():
                if group_name not in result or not result[group_name]:
                    for block in blocks:
                        m = re.fullmatch(pat, block)
                        if m:
                            result[group_name] = m.group(0)
                            break

        return result
