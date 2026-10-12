"""Функции для работы с серверами.

Серверы хранятся в словаре: ключ — идентификатор сервера,
значение — словарь с данными сервера (name, location, slots).
"""
from typing import Iterator


def get_free_slots(total: int, used: int) -> int:
    """Вернуть количество свободных слотов сервера (функция из ПР1)."""
    return max(total - used, 0)


def get_load_percent(total: int, used: int) -> float:
    """Вернуть загрузку сервера в процентах (функция из ПР1)."""
    if total == 0:
        return 100.0
    return round(used / total * 100, 1)


def get_load_level(load_percent: float) -> str:
    """Вернуть словесную оценку загрузки сервера (функция из ПР1)."""
    if load_percent < 50:
        return "низкая"
    if load_percent < 85:
        return "средняя"
    return "высокая"


def add_server(
    servers: dict[int, dict],
    name: str,
    location: str,
    slots: int,
) -> dict:
    """Добавить сервер в словарь servers и вернуть его данные.

    Идентификатор нового сервера на единицу больше максимального.
    Количество слотов должно быть положительным, иначе ValueError.
    """
    if slots <= 0:
        raise ValueError("Количество слотов должно быть больше нуля")
    server_id = max(servers, default=0) + 1
    server = {
        "id": server_id,
        "name": name,
        "location": location,
        "slots": slots,
    }
    servers[server_id] = server
    return server


def find_server(servers: dict[int, dict], query: str) -> list[dict]:
    """Найти серверы, в названии которых встречается подстрока query."""
    query = query.lower()
    return [
        server for server in servers.values()
        if query in server["name"].lower()
    ]


def check_server_slots(
    servers: dict[int, dict],
    server_id: int,
    min_slots: int,
) -> bool:
    """Проверить, что у сервера не меньше min_slots слотов."""
    server = servers.get(server_id)
    if server is None:
        return False
    return server["slots"] >= min_slots


def filter_servers_by_slots(
    servers: dict[int, dict],
    min_slots: int,
) -> Iterator[dict]:
    """Отобрать серверы, у которых не меньше min_slots слотов (генератор)."""
    for server in servers.values():
        if server["slots"] >= min_slots:
            yield server


def sort_servers(
    servers: dict[int, dict],
    reverse: bool = False,
) -> list[dict]:
    """Вернуть серверы, упорядоченные по количеству слотов."""
    return sorted(
        servers.values(),
        key=lambda server: server["slots"],
        reverse=reverse,
    )
