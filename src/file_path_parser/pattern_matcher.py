__all__ = ['PatternMatcher']

import re
from datetime import datetime
from typing import Iterable, Optional, Dict


class PatternMatcher:
    """
        Класс для поиска по регулярным выражениям.
        Содержит встроенные паттерны для даты и времени и поддерживает пользовательские шаблоны.
    """
    DATE_PATTERNS = [
        r'\d{8}',                             # 20240622
        r'\b\d{4}[-_]\d{2}[-_]\d{2}\b',       # 2024-06-22, 2024_06_22
        r'\b\d{2}[.-_]\d{2}[.-_]\d{4}\b',     # 22.06.2024, 22-06-2024
        r'\b\d{6}\b',                         # 220624
        r'\b\d{4}[-_]\d{1,2}[-_]\d{1,2}\b',   # 2024-6-22, 2024_6_2
    ]
    TIME_PATTERNS = [
        r'\d{6}',                             # 154212
        r'\d{4}',                             # 1542
        r'\b\d{2}[-_]\d{2}[-_]\d{2}\b',       # 15-42-12, 15_42_12
        r'\b\d{2}[-_]\d{2}\b',                # 15-42, 15_42
    ]

    def __init__(self, user_patterns: Optional[Dict[str, str]] = None):
        """
            Args:
                user_patterns: дополнительные шаблоны для поиска, например {"cam": r"cam\d{1,3}"}
        """
        self.user_patterns = user_patterns or {}

    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        """ Проверяет, что строка — валидная дата. """
        for fmt in ("%Y%m%d", "%Y-%m-%d", "%Y_%m_%d", "%d.%m.%Y", "%d-%m-%Y", "%y%m%d"):
            try:
                datetime.strptime(date_str, fmt)
                return True
            except ValueError:
                continue
        return False

    @staticmethod
    def is_valid_time(time_str: str) -> bool:
        """ Проверяет, что строка — валидное время. """
        for fmt in ("%H%M%S", "%H%M", "%H-%M-%S", "%H_%M_%S", "%H-%M", "%H_%M"):
            try:
                datetime.strptime(time_str, fmt)
                return True
            except ValueError:
                continue
        return False

    def find_special(self, s: str, key: str) -> Optional[str]:
        """ Ищет специальные группы: date, time, либо кастомные шаблоны. """
        if key.lower() == "date":
            return self._find_by_patterns(s, self.DATE_PATTERNS)
        if key.lower() == "time":
            return self._find_by_patterns(s, self.TIME_PATTERNS)
        if key in self.user_patterns:
            return self._find_by_patterns(s, [self.user_patterns[key]])
        return None

    def _find_by_patterns(self, s: str, patterns: Iterable[str]) -> Optional[str]:
        """ Возвращает первую группу, если она есть, иначе весь матч """
        for pat in patterns:
            # Авто-оборачивание для case cam\d+ → cam(\d+)
            patched_pat = pat
            if "(" not in pat:
                patched_pat = self.__wrap_digit_pattern(pat)
            found = re.search(patched_pat, s)
            if found:
                return found.group(1) if found.lastindex else found.group(0)
        return None

    def __wrap_digit_pattern(self, pat):
        # Заменяет все варианты \d+ или \d{...} на (\d+) или (\d{...})
        return re.sub(r'(\\d(\{\d+(,\d+)?\}|\+))', r'(\1)', pat)
