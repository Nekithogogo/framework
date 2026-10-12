"""Функции для работы с оборудованием, его характеристиками и состоянием.

Оборудование хранится в списке словарей. Каждый словарь содержит
идентификатор, название, тип, серийный номер, идентификатор сервера
(None — оборудование не установлено), дату установки, код состояния
и список характеристик.
"""
from datetime import date
from typing import Optional

from servers import get_free_slots

STATES = {
    "working": "исправно",
    "faulty": "неисправно",
    "repair": "в ремонте",
    "decommissioned": "списано",
}
WORKING_STATE = "working"
DECOMMISSIONED_STATE = "decommissioned"


def add_equipment(
    equipment: list[dict],
    name: str,
    kind: str,
    serial_number: str,
    state: str = WORKING_STATE,
) -> dict:
    """Добавить оборудование в список и вернуть его данные.

    Серийный номер должен быть уникальным, состояние — одним из STATES.
    """
    if state not in STATES:
        raise ValueError(f"Неизвестное состояние: {state}")
    if any(item["serial_number"] == serial_number for item in equipment):
        raise ValueError(f"Серийный номер {serial_number} уже учтен")
    item = {
        "id": max((item["id"] for item in equipment), default=0) + 1,
        "name": name,
        "kind": kind,
        "serial_number": serial_number,
        "server_id": None,
        "installed_at": None,
        "state": state,
        "characteristics": [],
    }
    equipment.append(item)
    return item


def find_equipment(equipment: list[dict], query: str) -> list[dict]:
    """Найти оборудование по подстроке названия или серийного номера."""
    query = query.lower()
    return [
        item for item in equipment
        if query in item["name"].lower()
        or query in item["serial_number"].lower()
    ]


def find_equipment_by_id(
    equipment: list[dict],
    equipment_id: int,
) -> Optional[dict]:
    """Найти оборудование по идентификатору."""
    for item in equipment:
        if item["id"] == equipment_id:
            return item
    return None


def add_characteristic(
    item: dict,
    name: str,
    value: str,
    unit: str = "",
) -> None:
    """Добавить характеристику оборудованию.

    Если характеристика с таким названием уже есть, ее значение
    заменяется новым.
    """
    for characteristic in item["characteristics"]:
        if characteristic["name"].lower() == name.lower():
            characteristic["value"] = value
            characteristic["unit"] = unit
            return
    item["characteristics"].append(
        {"name": name, "value": value, "unit": unit}
    )


def get_server_equipment(equipment: list[dict], server_id: int) -> list[dict]:
    """Вернуть оборудование, установленное в сервер."""
    return [item for item in equipment if item["server_id"] == server_id]


def count_installed(equipment: list[dict], server_id: int) -> int:
    """Посчитать количество занятых слотов сервера."""
    return len(get_server_equipment(equipment, server_id))


def has_free_slot(
    servers: dict[int, dict],
    equipment: list[dict],
    server_id: int,
) -> bool:
    """Проверить, есть ли у сервера свободный слот."""
    server = servers.get(server_id)
    if server is None:
        return False
    used = count_installed(equipment, server_id)
    return get_free_slots(server["slots"], used) > 0


def can_install(free_slots: int, state: str) -> bool:
    """Проверить возможность установки (функция из ПР1).

    Установка возможна, если у сервера есть свободный слот,
    а оборудование исправно.
    """
    return free_slots > 0 and state == WORKING_STATE


def get_install_status(is_possible: bool) -> str:
    """Вернуть текстовый статус установки (функция из ПР1)."""
    if is_possible:
        return "Оборудование можно установить в сервер"
    return "Установка невозможна"


def install_equipment(
    servers: dict[int, dict],
    equipment: list[dict],
    equipment_id: int,
    server_id: int,
    installed_at: date,
) -> dict:
    """Установить оборудование в сервер и вернуть его данные.

    При нарушении правил установки возбуждается ValueError
    с описанием причины.
    """
    item = find_equipment_by_id(equipment, equipment_id)
    if item is None:
        raise ValueError("Оборудование не найдено")
    server = servers.get(server_id)
    if server is None:
        raise ValueError("Сервер не найден")
    if item["server_id"] is not None:
        raise ValueError("Оборудование уже установлено в сервер")
    if item["state"] != WORKING_STATE:
        raise ValueError("Установить можно только исправное оборудование")
    used = count_installed(equipment, server_id)
    if not can_install(get_free_slots(server["slots"], used), item["state"]):
        raise ValueError("В сервере нет свободных слотов")
    item["server_id"] = server_id
    item["installed_at"] = installed_at.isoformat()
    return item


def uninstall_equipment(equipment: list[dict], equipment_id: int) -> bool:
    """Снять оборудование с сервера.

    Возвращает True, если оборудование было установлено и снято.
    """
    item = find_equipment_by_id(equipment, equipment_id)
    if item is None or item["server_id"] is None:
        return False
    item["server_id"] = None
    item["installed_at"] = None
    return True


def change_state(
    equipment: list[dict],
    equipment_id: int,
    state: str,
) -> bool:
    """Изменить состояние оборудования.

    Списанное оборудование автоматически снимается с сервера.
    Возвращает False, если оборудование не найдено.
    """
    if state not in STATES:
        raise ValueError(f"Неизвестное состояние: {state}")
    item = find_equipment_by_id(equipment, equipment_id)
    if item is None:
        return False
    item["state"] = state
    if state == DECOMMISSIONED_STATE:
        uninstall_equipment(equipment, equipment_id)
    return True
