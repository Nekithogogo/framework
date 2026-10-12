"""RackKeeper — консольное приложение учета серверного оборудования.

Точка запуска программы: меню и пользовательские сценарии.
Каждый пункт меню — функция с общей сигнатурой (servers, states,
equipment). Текст пункта меню берется из документации функции.
"""
import os
from typing import Callable, List, Optional

from models import Characteristic, Equipment, Server, State
from models.equipment import (
    add_equipment,
    can_install,
    change_equipment_state,
    count_by_server,
    count_installed,
    find_equipment,
    find_equipment_by_id,
    get_install_status,
    get_server_equipment,
    install_equipment,
    show_equipment,
    uninstall_equipment,
)
from models.servers import (
    add_server,
    filter_servers_by_slots,
    find_server,
    find_server_by_id,
    show_servers,
    sort_servers,
)
from models.states import find_state_by_id, show_states
from storage import (
    load_equipment,
    load_servers,
    load_states,
    save_equipment,
    save_servers,
)
from utils import input_choice, input_date, input_int, input_text

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SERVERS_FILE = os.path.join(DATA_DIR, "servers.json")
STATES_FILE = os.path.join(DATA_DIR, "states.json")
EQUIPMENT_FILE = os.path.join(DATA_DIR, "equipment.json")

Action = Callable[[List[Server], List[State], List[Equipment]], None]


def save_all(servers: List[Server], equipment: List[Equipment]) -> None:
    """Сохранить изменяемые данные проекта в JSON-файлы."""
    save_servers(SERVERS_FILE, servers)
    save_equipment(EQUIPMENT_FILE, equipment)


def select_server(servers: List[Server]) -> Optional[Server]:
    """Запросить ID и найти сервер; сообщить, если его нет."""
    server = find_server_by_id(servers, input_int("ID сервера: "))
    if server is None:
        print("Сервер не найден")
    return server


def select_equipment(equipment: List[Equipment]) -> Optional[Equipment]:
    """Запросить ID и найти оборудование; сообщить, если его нет."""
    item = find_equipment_by_id(equipment, input_int("ID оборудования: "))
    if item is None:
        print("Оборудование не найдено")
    return item


def select_state(states: List[State]) -> State:
    """Предложить выбрать состояние из справочника."""
    options = {state.id: state.name for state in states}
    state_id = input_choice("Состояние: ", options)
    state = find_state_by_id(states, state_id)
    assert state is not None
    return state


def print_servers(
    servers: List[Server],
    states: List[State],
    equipment: List[Equipment],
) -> None:
    """Показать серверы"""
    show_servers(sort_servers(servers, reverse=True),
                 count_by_server(equipment))


def search_servers(
    servers: List[Server],
    states: List[State],
    equipment: List[Equipment],
) -> None:
    """Найти сервер по названию"""
    query = input_text("Часть названия: ")
    show_servers(find_server(servers, query), count_by_server(equipment))


def select_servers(
    servers: List[Server],
    states: List[State],
    equipment: List[Equipment],
) -> None:
    """Отобрать серверы по количеству слотов"""
    min_slots = input_int("Минимальное количество слотов: ", min_value=1)
    show_servers(list(filter_servers_by_slots(servers, min_slots)),
                 count_by_server(equipment))


def create_server(
    servers: List[Server],
    states: List[State],
    equipment: List[Equipment],
) -> None:
    """Добавить сервер"""
    name = input_text("Название сервера: ")
    location = input_text("Расположение (стойка): ")
    slots = input_int("Количество слотов: ", min_value=1)
    server = add_server(servers, name, location, slots)
    save_all(servers, equipment)
    print(f"Сервер добавлен: {server}")


def print_equipment(
    servers: List[Server],
    states: List[State],
    equipment: List[Equipment],
) -> None:
    """Показать оборудование"""
    show_equipment(equipment)


def print_server_equipment(
    servers: List[Server],
    states: List[State],
    equipment: List[Equipment],
) -> None:
    """Показать оборудование сервера"""
    server = select_server(servers)
    if server is not None:
        print(server)
        show_equipment(get_server_equipment(equipment, server))


def search_equipment(
    servers: List[Server],
    states: List[State],
    equipment: List[Equipment],
) -> None:
    """Найти оборудование по названию или серийному номеру"""
    query = input_text("Строка поиска: ")
    show_equipment(find_equipment(equipment, query))


def create_equipment(
    servers: List[Server],
    states: List[State],
    equipment: List[Equipment],
) -> None:
    """Добавить оборудование"""
    name = input_text("Название: ")
    kind = input_text("Тип (CPU, RAM, SSD, ...): ")
    serial_number = input_text("Серийный номер: ")
    state = select_state(states)
    try:
        item = add_equipment(equipment, name, kind, serial_number, state)
    except ValueError as error:
        print(error)
        return
    save_all(servers, equipment)
    print(f"Оборудование добавлено: {item}")


def create_characteristic(
    servers: List[Server],
    states: List[State],
    equipment: List[Equipment],
) -> None:
    """Добавить характеристику оборудованию"""
    item = select_equipment(equipment)
    if item is None:
        return
    name = input_text("Характеристика (например, Объем): ")
    value = input_text("Значение: ")
    unit = input("Единица измерения (можно пропустить): ").strip()
    item.add_characteristic(Characteristic(name, value, unit))
    save_all(servers, equipment)
    print("Характеристика сохранена")


def check_install(
    servers: List[Server],
    states: List[State],
    equipment: List[Equipment],
) -> None:
    """Проверить возможность установки в сервер"""
    server = select_server(servers)
    item = select_equipment(equipment)
    if server is None or item is None:
        return
    free = server.get_free_slots(count_installed(equipment, server))
    print(f"Свободных слотов в {server.name}: {free}")
    print(f"Состояние оборудования: {item.state}")
    is_possible = can_install(free, item.state) and not item.is_installed
    if item.is_installed:
        print("Оборудование уже установлено в сервер")
    print(get_install_status(is_possible))


def install(
    servers: List[Server],
    states: List[State],
    equipment: List[Equipment],
) -> None:
    """Установить оборудование в сервер"""
    item = select_equipment(equipment)
    server = select_server(servers)
    if item is None or server is None:
        return
    installed_at = input_date("Дата установки ДД.ММ.ГГГГ (Enter — сегодня): ")
    try:
        install_equipment(equipment, item, server, installed_at)
    except ValueError as error:
        print(f"{get_install_status(False)}: {error}")
        return
    save_all(servers, equipment)
    print(f"Установлено: {item}")


def uninstall(
    servers: List[Server],
    states: List[State],
    equipment: List[Equipment],
) -> None:
    """Снять оборудование с сервера"""
    if uninstall_equipment(equipment, input_int("ID оборудования: ")):
        save_all(servers, equipment)
        print("Оборудование снято с сервера")
    else:
        print("Оборудование не найдено или не установлено")


def update_state(
    servers: List[Server],
    states: List[State],
    equipment: List[Equipment],
) -> None:
    """Изменить состояние оборудования"""
    equipment_id = input_int("ID оборудования: ")
    state = select_state(states)
    if change_equipment_state(equipment, equipment_id, state):
        save_all(servers, equipment)
        print(f"Состояние изменено: {state}")
    else:
        print("Оборудование не найдено")


def print_states(
    servers: List[Server],
    states: List[State],
    equipment: List[Equipment],
) -> None:
    """Показать справочник состояний"""
    show_states(states)


ACTIONS: dict[str, Action] = {
    "1": print_servers,
    "2": search_servers,
    "3": select_servers,
    "4": create_server,
    "5": print_equipment,
    "6": print_server_equipment,
    "7": search_equipment,
    "8": create_equipment,
    "9": create_characteristic,
    "10": check_install,
    "11": install,
    "12": uninstall,
    "13": update_state,
    "14": print_states,
}


def print_menu() -> None:
    """Вывести меню, используя документацию функций-действий."""
    print("\n=== RackKeeper: учет серверного оборудования ===")
    for key, action in ACTIONS.items():
        print(f"{key}. {action.__doc__}")
    print("0. Выход")


def main() -> None:
    """Точка запуска: загрузка объектов, цикл меню, сохранение."""
    servers = load_servers(SERVERS_FILE)
    states = load_states(STATES_FILE)
    equipment = load_equipment(EQUIPMENT_FILE, servers, states)
    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()
        if choice == "0":
            break
        action = ACTIONS.get(choice)
        if action is None:
            print("Такого пункта нет")
            continue
        print()
        action(servers, states, equipment)
    save_all(servers, equipment)


if __name__ == "__main__":
    main()
