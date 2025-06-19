__all__ = ['PathNameParser']

import re
from pathlib import Path
from typing import Dict, Any, Union

from pattern_matcher import PatternMatcher


class PathNameParser:
    """
        Универсальный парсер для извлечения групп (factory, module, date, time, и любые custom patterns)
        из имени файла или пути.
        - Передайте groups: словарь {"ключ": Enum/список/True} для поиска известных значений (enums, списки)
          и спец-флагов ("date", "time").
        - Передайте patterns: словарь {"ключ": regex-строка} для поиска по регулярным выражениям.
        - separator: строка-разделитель (по умолчанию "_").
        - priority: "filename" (по умолчанию) или "path" — что считать приоритетным при объединении.
        Все ключи из patterns всегда ищутся и попадают в результат, даже если их нет в groups.
    """

    def __init__(
            self,
            groups: Dict[str, Any],
            separator: str = "_",
            priority: str = "filename",
            patterns: dict = None,
    ):
        """
            Args:
                groups: словарь {группа: список_значений или True/False для date/time}
                separator: символ-разделитель (по умолчанию "_")
                priority: что важнее: 'filename' или 'path'
                patterns: словарь дополнительных паттернов (regex), например {"cam": r"cam\d{1,3}"}
        """
        self._groups = groups
        self._separator = separator
        self._priority = priority
        self._enum_groups = {k: v for k, v in groups.items() if not isinstance(v, bool)}
        self._special_groups = {k: v for k, v in groups.items() if isinstance(v, bool)}
        self.matcher = PatternMatcher(patterns)

    def parse(self, full_path: Union[str, Path]) -> dict:
        """ Анализирует путь или имя файла, возвращает словарь найденных групп. """
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

    def _parse_blocks(self, s: str) -> dict:
        blocks = [b for b in re.split(r'[\\/{}\-_. ]+', s) if b]
        result = {}

        # Обычные группы (enum, list)
        for group_name, group_values in self._enum_groups.items():
            found = None
            values = self._to_str_list(group_values)
            for value in values:
                for block in blocks:
                    if value and value == block:
                        found = value
                        break
                if found:
                    break
            result[group_name] = found

        # Дата
        date_val = None
        if "date" in self._special_groups and self._special_groups["date"]:
            for b in blocks:
                for pat in self.matcher.DATE_PATTERNS:
                    m = re.fullmatch(pat, b)
                    if m and self.matcher.is_valid_date(m.group(0)):
                        date_val = m.group(0)
                        break
                if date_val:
                    break
            result["date"] = date_val

        # Время (исключая блок, уже найденный как дата)
        time_val = None
        if "time" in self._special_groups and self._special_groups["time"]:
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

        # Пользовательские шаблоны (patterns)
        if self.matcher.user_patterns:
            for group_name, pat in self.matcher.user_patterns.items():
                if group_name not in result or not result[group_name]:
                    for block in blocks:
                        m = re.fullmatch(pat, block)
                        if m:
                            result[group_name] = m.group(0)
                            break

        return result

    @staticmethod
    def _to_str_list(values):
        if hasattr(values, "__members__"):  # Enum class
            return [str(v.value) for v in values]
        if isinstance(values, dict):
            return list(map(str, values.values()))
        return [str(v) for v in values]
