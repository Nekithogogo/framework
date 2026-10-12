"""Загрузка и сохранение данных проекта в JSON-файлах.

JSON хранит только данные: при загрузке они превращаются в объекты
Server, State и Equipment, при сохранении — обратно в словари.
Связи оборудования с сервером и состоянием хранятся в JSON
как идентификаторы server_id и state_id.
"""
import json
import os
from datetime import date
from typing import Callable, List, Sequence, TypeVar

from models import Characteristic, Entity, Equipment, Server, State
from models.servers import find_server_by_id
from models.states import find_state_by_id

T = TypeVar("T")


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


def load_objects(filename: str, factory: Callable[[dict], T]) -> List[T]:
    """Загрузить объекты из JSON, пропуская некорректные записи."""
    objects = []
    for data in read_json(filename):
        try:
            objects.append(factory(data))
        except (KeyError, TypeError, ValueError) as error:
            print(f"{filename}: запись {data} пропущена ({error})")
    return objects


def save_objects(filename: str, objects: Sequence[Entity]) -> None:
    """Сохранить объекты любого класса-наследника Entity.

    Каждый объект сам знает, как превратиться в словарь (to_dict).
    """
    write_json(filename, [item.to_dict() for item in objects])


def load_servers(filename: str) -> List[Server]:
    """Загрузить серверы: JSON → объекты Server."""
    return load_objects(filename, Server.from_data)


def save_servers(filename: str, servers: List[Server]) -> None:
    """Сохранить серверы: объекты Server → JSON."""
    save_objects(filename, servers)


def load_states(filename: str) -> List[State]:
    """Загрузить справочник состояний: JSON → объекты State."""
    return load_objects(filename, State.from_data)


def save_states(filename: str, states: List[State]) -> None:
    """Сохранить справочник состояний."""
    save_objects(filename, states)


def load_equipment(
    filename: str,
    servers: List[Server],
    states: List[State],
) -> List[Equipment]:
    """Загрузить оборудование и восстановить связи с Server и State.

    Если сервер или состояние с указанным идентификатором не найдены,
    запись не превращается в объект и пропускается.
    """

    def make_equipment(data: dict) -> Equipment:
        state = find_state_by_id(states, data["state_id"])
        if state is None:
            raise ValueError(f"нет состояния {data['state_id']}")
        server = None
        if data.get("server_id") is not None:
            server = find_server_by_id(servers, data["server_id"])
            if server is None:
                raise ValueError(f"нет сервера {data['server_id']}")
        installed_at = data.get("installed_at")
        return Equipment(
            equipment_id=data["id"],
            name=data["name"],
            kind=data["kind"],
            serial_number=data["serial_number"],
            state=state,
            server=server,
            installed_at=(
                date.fromisoformat(installed_at) if installed_at else None
            ),
            characteristics=[
                Characteristic.from_data(item)
                for item in data.get("characteristics", [])
            ],
        )

    return load_objects(filename, make_equipment)


def save_equipment(filename: str, equipment: List[Equipment]) -> None:
    """Сохранить оборудование: ссылки на объекты → идентификаторы."""
    save_objects(filename, equipment)
