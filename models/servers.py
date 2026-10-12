"""Класс Server и функции работы с коллекцией серверов."""
from typing import Iterator, List, Optional

from .base import Entity


class Server(Entity):
    """Сервер, в слоты которого устанавливается оборудование."""

    def __init__(
        self,
        server_id: int,
        name: str,
        location: str,
        slots: int,
    ) -> None:
        """Создать объект сервера."""
        super().__init__(server_id)
        self.name = name
        self.location = location
        self.slots = slots

    @property
    def slots(self) -> int:
        """Количество слотов сервера."""
        return self._slots

    @slots.setter
    def slots(self, value: int) -> None:
        """Изменить количество слотов, проверив корректность значения."""
        if not Server.validate_slots(value):
            raise ValueError("Количество слотов должно быть больше нуля")
        self._slots = value

    @staticmethod
    def validate_slots(slots: int) -> bool:
        """Проверить корректность количества слотов."""
        return isinstance(slots, int) and slots > 0

    @staticmethod
    def get_load_level(load_percent: float) -> str:
        """Вернуть словесную оценку загрузки (логика из ПР1)."""
        if load_percent < 50:
            return "низкая"
        if load_percent < 85:
            return "средняя"
        return "высокая"

    def is_suitable_for(self, required_slots: int) -> bool:
        """Проверить, что у сервера не меньше required_slots слотов."""
        return self.slots >= required_slots

    def get_free_slots(self, used: int) -> int:
        """Вернуть количество свободных слотов при used занятых."""
        return max(self.slots - used, 0)

    def get_load_percent(self, used: int) -> float:
        """Вернуть загрузку сервера в процентах при used занятых слотах."""
        return round(used / self.slots * 100, 1)

    @classmethod
    def from_data(cls, data: dict) -> "Server":
        """Создать сервер из словаря данных JSON."""
        return cls(data["id"], data["name"], data["location"], data["slots"])

    def to_dict(self) -> dict:
        """Вернуть данные сервера для сохранения в JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "slots": self.slots,
        }

    def __str__(self) -> str:
        """Вернуть строковое представление сервера."""
        return f"{self.name} ({self.location}, слотов: {self.slots})"


def add_server(
    servers: List[Server],
    name: str,
    location: str,
    slots: int,
) -> Server:
    """Создать сервер, добавить его в коллекцию и вернуть."""
    server_id = max((server.id for server in servers), default=0) + 1
    server = Server(server_id, name, location, slots)
    servers.append(server)
    return server


def find_server(servers: List[Server], query: str) -> List[Server]:
    """Найти серверы, в названии которых встречается подстрока query."""
    query = query.lower()
    return [server for server in servers if query in server.name.lower()]


def find_server_by_id(
    servers: List[Server],
    server_id: int,
) -> Optional[Server]:
    """Найти сервер по идентификатору."""
    for server in servers:
        if server.id == server_id:
            return server
    return None


def check_server_slots(
    servers: List[Server],
    server_id: int,
    min_slots: int,
) -> bool:
    """Найти сервер и проверить, что у него не меньше min_slots слотов."""
    server = find_server_by_id(servers, server_id)
    return server is not None and server.is_suitable_for(min_slots)


def filter_servers_by_slots(
    servers: List[Server],
    min_slots: int,
) -> Iterator[Server]:
    """Отобрать серверы, у которых не меньше min_slots слотов (генератор)."""
    for server in servers:
        if server.is_suitable_for(min_slots):
            yield server


def sort_servers(servers: List[Server], reverse: bool = False) -> List[Server]:
    """Вернуть серверы, упорядоченные по количеству слотов."""
    return sorted(servers, key=lambda server: server.slots, reverse=reverse)


def show_servers(servers: List[Server], used_slots: dict[int, int]) -> None:
    """Вывести таблицу серверов с загрузкой.

    used_slots — количество занятых слотов по идентификаторам серверов.
    """
    if not servers:
        print("Серверы не найдены")
        return
    print(f"{'ID':>3}  {'Название':<16}{'Расположение':<14}"
          f"{'Слоты':>7}  Загрузка")
    for server in servers:
        used = used_slots.get(server.id, 0)
        load = server.get_load_percent(used)
        print(f"{server.id:>3}  {server.name:<16}{server.location:<14}"
              f"{used:>3}/{server.slots:<3}  "
              f"{load}% ({Server.get_load_level(load)})")
