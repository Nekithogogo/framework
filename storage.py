"""Загрузка и сохранение данных проекта в JSON-файлах."""
import json
import os


def read_json(filename: str) -> list:
    """Прочитать список записей из JSON-файла.

    Отсутствующий файл считается пустым списком. При поврежденном
    файле выводится предупреждение и также возвращается пустой список.
    """
    try:
        with open(filename, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        print(f"Файл {filename} поврежден ({error}), данные не загружены")
        return []
    if not isinstance(data, list):
        print(f"Файл {filename} должен содержать список записей")
        return []
    return data


def write_json(filename: str, data: list) -> None:
    """Записать список записей в JSON-файл."""
    folder = os.path.dirname(filename)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_servers(filename: str) -> dict[int, dict]:
    """Загрузить серверы из JSON-файла в словарь по идентификаторам."""
    return {server["id"]: server for server in read_json(filename)}


def save_servers(filename: str, servers: dict[int, dict]) -> None:
    """Сохранить серверы в JSON-файл."""
    write_json(filename, list(servers.values()))


def load_equipment(filename: str) -> list[dict]:
    """Загрузить оборудование из JSON-файла."""
    return read_json(filename)


def save_equipment(filename: str, equipment: list[dict]) -> None:
    """Сохранить оборудование в JSON-файл."""
    write_json(filename, equipment)
