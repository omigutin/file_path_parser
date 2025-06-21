# run.py — ручной запуск и примеры FilePathParser

from src.file_path_parser import FilePathParser


if __name__ == "__main__":
    print("=== DEMO: FilePathParser ===")

    parser = FilePathParser(
        ["cat", "dog"],
        ["night", "day"],
        date=True,
        time=True,
        patterns={"cam": r"cam\d{1,3}"}
    )

    test_path = "cat_night_cam15_20240619_1236.jpg"
    result = parser.parse(test_path)
    print(f"Parsing: {test_path}")
    print(result)
