__all__ = ['FilePathParser']

import re
from typing import Any, Dict, List, Optional, Union, Iterable

from pathlib import Path

from .pattern_matcher import PatternMatcher


class FilePathParser:
    """
        Универсальный парсер для извлечения групп, дат, времени и кастомных шаблонов
        из имени файла или пути.

        Пример:
            parser = FilePathParser(
                ["cat", "dog"],
                ["night", "day"],
                date=True,
                time=True,
                patterns={"cam": r"cam\d{1,3}"}
            )
            out = parser.parse("cat_night_cam15_20240619_1236.jpg")
            # out == {"group1": "cat", "group2": "night", "date": "20240619", "time": "1236", "cam": "cam15"}
    """
    _groups: Dict[str, Dict[str, str]]
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
            merged = dict(data_from_name)
            for k, v in data_from_path.items():
                if not merged.get(k):
                    merged[k] = v
        elif self._priority == "path":
            merged = dict(data_from_path)
            for k, v in data_from_name.items():
                if not merged.get(k):
                    merged[k] = v
        else:
            raise ValueError(f"Unknown priority: {self._priority}")

        return merged

    @staticmethod
    def _parse_groups(*groups: Any) -> Dict[str, Dict[str, str]]:
        """
            Преобразует все пришедшие группы в словарь {group_name: {value_lower: value_original}}.
            Args:
                *groups: любые списки, enum, dict, str

            Returns:
                dict: {group_name: {value_lower: value_original}}
        """
        result: Dict[str, Dict[str, str]] = {}
        group_counter = 1
        for g in groups:
            if hasattr(g, "__members__"):  # Enum
                name = g.__name__.lower()
                result[name] = {str(v.value).lower(): str(v.value) for v in g}
            elif isinstance(g, dict):
                for k, v in g.items():
                    name = str(k).lower()
                    values = v if isinstance(v, (list, tuple, set)) else [v]
                    result[name] = {str(val).lower(): str(val) for val in values}
            elif isinstance(g, (list, tuple, set)):
                name = f"group{group_counter}"
                result[name] = {str(val).lower(): str(val) for val in g}
                group_counter += 1
            elif isinstance(g, str):
                name = g.lower()
                result[name] = {g.lower(): g}
            else:
                name = g.__class__.__name__.lower()
                result[name] = {str(g).lower(): str(g)}
        return result

    def _parse_blocks(self, s: str) -> Dict[str, Optional[str]]:
        """
            Разбивает входную строку на блоки и последовательно извлекает из них
            группы, дату, время и кастомные паттерны.
            Args:
                s (str): Имя файла или путь, содержащий информативные блоки.
            Returns:
                Dict[str, Optional[str]]: Словарь, где ключи — имена групп, "date", "time" и имена кастомных паттернов,
                а значения — найденные совпадения (или None, если не найдено).
        """
        blocks = [b.lower() for b in re.split(r'[\\/{}\-_. ]+', s) if b]
        result: Dict[str, Optional[str]] = {}

        # Группы
        result.update(self._find_groups(blocks))

        # Дата
        date_val = self._find_date(blocks) if self._date else None
        if date_val:
            result["date"] = date_val

        # Время
        time_val = self._find_time(blocks, exclude=date_val) if self._time else None
        if time_val:
            result["time"] = time_val

        # Кастомные patterns
        result.update(self._find_patterns(blocks, skip_keys=result.keys()))

        return result

    def _find_groups(self, blocks: List[str]) -> Dict[str, Optional[str]]:
        """
            Ищет совпадения между переданными группами значений и блоками строки.
            Возвращает оригинальное значение (а не lower-case).
            Args:
                blocks (List[str]): Список строковых блоков, полученных из имени файла или пути.
            Returns:
                Dict[str, Optional[str]]: Словарь, где ключи — имена групп, значения — найденный элемент или None.
        """
        res = {}
        for group_name, group_values in self._groups.items():
            found = None
            for block in blocks:
                key = block.lower()
                if key in group_values:
                    found = group_values[key]
                    break
            res[group_name] = found
        return res

    def _find_date(self, blocks: List[str]) -> Optional[str]:
        """
            Ищет блок, соответствующий одному из поддерживаемых форматов даты, и валидирует его.
            Args:
                blocks (List[str]): Список строковых блоков для анализа.
            Returns:
                Optional[str]: Найденная валидная дата в виде строки, либо None если не найдено.
        """
        for b in blocks:
            for pat in self.matcher.DATE_PATTERNS:
                m = re.fullmatch(pat, b)
                if m and self.matcher.is_valid_date(m.group(0)):
                    return m.group(0)
        return None

    def _find_time(self, blocks: List[str], exclude: Optional[str] = None) -> Optional[str]:
        """
            Ищет блок, соответствующий одному из поддерживаемых форматов времени, с опциональным исключением блока даты.
            Args:
                blocks (List[str]): Список строковых блоков для анализа.
                exclude (Optional[str]): Значение, которое не должно рассматриваться как время (например, найденная дата).
            Returns:
                Optional[str]: Найденное валидное время в виде строки, либо None если не найдено.
        """
        for b in blocks:
            if b == exclude:
                continue
            for pat in self.matcher.TIME_PATTERNS:
                m = re.fullmatch(pat, b)
                if m and self.matcher.is_valid_time(m.group(0)):
                    return m.group(0)
        return None

    def _find_patterns(self, blocks: List[str], skip_keys: Optional[Iterable[str]] = None) -> Dict[str, Optional[str]]:
        """
            Ищет пользовательские кастомные паттерны по всем блокам.
            Args:
                blocks (List[str]): Список строковых блоков.
                skip_keys (Optional[Iterable[str]]): Множество ключей, которые не нужно переопределять, если совпадение уже найдено.
            Returns:
                Dict[str, Optional[str]]: Словарь с именами паттернов и найденными значениями (или None).
        """
        skip_keys = set(skip_keys) if skip_keys else set()
        res = {}
        if self.matcher.user_patterns:
            for group_name, pat in self.matcher.user_patterns.items():
                if group_name in skip_keys:
                    continue
                for block in blocks:
                    m = re.fullmatch(pat, block)
                    if m:
                        # Если паттерн содержит группу — вернуть только её содержимое
                        res[group_name] = m.group(1) if m.lastindex else m.group(0)
                        break
        return res
