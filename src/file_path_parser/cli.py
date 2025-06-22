import argparse

from .file_path_parser import FilePathParser


def main():
    parser = argparse.ArgumentParser(
        description="CLI для FilePathParser — извлечение структурированной информации из имён файлов."
    )
    parser.add_argument(
        "filepath",
        type=str,
        help="Путь к файлу или имя файла для парсинга"
    )
    parser.add_argument(
        "--groups",
        nargs="+",
        help="Список допустимых групп (через пробел), например: cat dog"
    )
    parser.add_argument(
        "--classes",
        nargs="+",
        help="Список допустимых классов (через пробел), например: night day"
    )
    parser.add_argument(
        "--date",
        action="store_true",
        help="Искать дату в имени файла"
    )
    parser.add_argument(
        "--time",
        action="store_true",
        help="Искать время в имени файла"
    )
    parser.add_argument(
        "--pattern",
        nargs=2,
        metavar=('NAME', 'REGEX'),
        action='append',
        help="Кастомный паттерн: --pattern cam 'cam\\d{1,3}' (можно указывать несколько раз)"
    )

    args = parser.parse_args()

    # Соберём patterns в dict
    patterns = dict(args.pattern) if args.pattern else {}

    fpp = FilePathParser(
        args.groups or [],
        args.classes or [],
        date=args.date,
        time=args.time,
        patterns=patterns,
    )

    result = fpp.parse(args.filepath)
    print("Результат парсинга:")
    print(result)


if __name__ == "__main__":
    main()
