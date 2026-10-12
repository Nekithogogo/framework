"""Класс Equipment и функции работы с коллекцией оборудования."""
from datetime import date
from typing import List, Optional

from .base import Entity
from .characteristics import Characteristic
from .servers import Server
from .states import State


class Equipment(Entity):
    """Единица оборудования: процессор, модуль памяти, диск и т. п.

    Оборудование хранит ссылки на объекты State (текущее состояние)
    и Server (сервер, в который оно установлено, или None).
    """

    def __init__(
        self,
        equipment_id: int,
        name: str,
        kind: str,
        serial_number: str,
        state: State,
        server: Optional[Server] = None,
        installed_at: Optional[date] = None,
        characteristics: Optional[List[Characteristic]] = None,
    ) -> None:
        """Создать объект оборудования."""
        super().__init__(equipment_id)
        self.name = name
        self.kind = kind
        self.serial_number = serial_number
        self.state = state
        self.server = server
        self.installed_at = installed_at
        self.characteristics = characteristics or []

    @property
    def is_installed(self) -> bool:
        """Признак того, что оборудование установлено в сервер."""
        return self.server is not None

    @property
    def needs_attention(self) -> bool:
        """Оборудование неисправно или в ремонте (но не списано)."""
        return not self.state.is_working and not self.state.is_decommissioned

    def can_be_installed(self) -> bool:
        """Проверить, что оборудование исправно и еще не установлено."""
        return self.state.is_working and not self.is_installed

    def install(self, server: Server, installed_at: date) -> None:
        """Установить оборудование в сервер.

        Проверяет только состояние самого оборудования; наличие
        свободного слота проверяет функция install_equipment().
        """
        if self.is_installed:
            raise ValueError("Оборудование уже установлено в сервер")
        if not self.state.is_working:
            raise ValueError("Установить можно только исправное оборудование")
        self.server = server
        self.installed_at = installed_at

    def uninstall(self) -> bool:
        """Снять оборудование с сервера; False — если оно не установлено."""
        if not self.is_installed:
            return False
        self.server = None
        self.installed_at = None
        return True

    def change_state(self, state: State) -> None:
        """Изменить состояние; списанное оборудование снимается с сервера."""
        self.state = state
        if state.is_decommissioned:
            self.uninstall()

    def add_characteristic(self, characteristic: Characteristic) -> None:
        """Добавить характеристику или заменить одноименную."""
        current = self.get_characteristic(characteristic.name)
        if current is not None:
            self.characteristics.remove(current)
        self.characteristics.append(characteristic)

    def get_characteristic(self, name: str) -> Optional[Characteristic]:
        """Найти характеристику по названию без учета регистра."""
        for characteristic in self.characteristics:
            if characteristic.name.lower() == name.lower():
                return characteristic
        return None

    def to_dict(self) -> dict:
        """Вернуть данные для JSON: вместо объектов — их идентификаторы."""
        return {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "serial_number": self.serial_number,
            "server_id": self.server.id if self.server else None,
            "installed_at": (
                self.installed_at.isoformat() if self.installed_at else None
            ),
            "state_id": self.state.id,
            "characteristics": [c.to_dict() for c in self.characteristics],
        }

    def __str__(self) -> str:
        """Вернуть строковое представление оборудования."""
        place = self.server.name if self.server else "на складе"
        return (f"[{self.id}] {self.name} ({self.kind}), "
                f"S/N {self.serial_number} — {self.state}, {place}")


def add_equipment(
    equipment: List[Equipment],
    name: str,
    kind: str,
    serial_number: str,
    state: State,
) -> Equipment:
    """Создать оборудование, добавить его в коллекцию и вернуть.

    Серийный номер должен быть уникальным, иначе ValueError.
    """
    if any(item.serial_number == serial_number for item in equipment):
        raise ValueError(f"Серийный номер {serial_number} уже учтен")
    equipment_id = max((item.id for item in equipment), default=0) + 1
    item = Equipment(equipment_id, name, kind, serial_number, state)
    equipment.append(item)
    return item


def find_equipment(equipment: List[Equipment], query: str) -> List[Equipment]:
    """Найти оборудование по подстроке названия или серийного номера."""
    query = query.lower()
    return [
        item for item in equipment
        if query in item.name.lower()
        or query in item.serial_number.lower()
    ]


def find_equipment_by_id(
    equipment: List[Equipment],
    equipment_id: int,
) -> Optional[Equipment]:
    """Найти оборудование по идентификатору."""
    for item in equipment:
        if item.id == equipment_id:
            return item
    return None


def get_server_equipment(
    equipment: List[Equipment],
    server: Server,
) -> List[Equipment]:
    """Вернуть оборудование, установленное в сервер."""
    return [item for item in equipment if item.server is server]


def count_installed(equipment: List[Equipment], server: Server) -> int:
    """Посчитать занятые слоты сервера."""
    return len(get_server_equipment(equipment, server))


def count_by_server(equipment: List[Equipment]) -> dict[int, int]:
    """Посчитать занятые слоты для всех серверов сразу."""
    result: dict[int, int] = {}
    for item in equipment:
        if item.server is not None:
            result[item.server.id] = result.get(item.server.id, 0) + 1
    return result


def has_free_slot(equipment: List[Equipment], server: Server) -> bool:
    """Проверить, есть ли у сервера свободный слот."""
    used = count_installed(equipment, server)
    return server.get_free_slots(used) > 0


def can_install(free_slots: int, state: State) -> bool:
    """Проверить возможность установки (функция из ПР1)."""
    return free_slots > 0 and state.is_working


def get_install_status(is_possible: bool) -> str:
    """Вернуть текстовый статус установки (функция из ПР1)."""
    if is_possible:
        return "Оборудование можно установить в сервер"
    return "Установка невозможна"


def install_equipment(
    equipment: List[Equipment],
    item: Equipment,
    server: Server,
    installed_at: date,
) -> Equipment:
    """Установить оборудование в сервер и вернуть его.

    При нарушении правил возбуждается ValueError с причиной.
    """
    if not has_free_slot(equipment, server):
        raise ValueError("В сервере нет свободных слотов")
    item.install(server, installed_at)
    return item


def uninstall_equipment(equipment: List[Equipment], equipment_id: int) -> bool:
    """Найти оборудование и снять его с сервера."""
    item = find_equipment_by_id(equipment, equipment_id)
    return item is not None and item.uninstall()


def change_equipment_state(
    equipment: List[Equipment],
    equipment_id: int,
    state: State,
) -> bool:
    """Найти оборудование и изменить его состояние."""
    item = find_equipment_by_id(equipment, equipment_id)
    if item is None:
        return False
    item.change_state(state)
    return True


def show_equipment(equipment: List[Equipment]) -> None:
    """Вывести список оборудования с характеристиками."""
    if not equipment:
        print("Оборудование не найдено")
        return
    for item in equipment:
        print(item)
        for characteristic in item.characteristics:
            print(f"      {characteristic}")
