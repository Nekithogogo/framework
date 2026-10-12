"""RackKeeper — консольное приложение учета серверного оборудования.

Точка запуска программы: меню и вызов функций проекта.
Каждый пункт меню — функция с общей сигнатурой (servers, equipment).
Текст пункта меню берется из первой строки документации функции.
"""
import os
from typing import Callable

from equipment import (
    STATES,
    add_characteristic,
    add_equipment,
    can_install,
    change_state,
    count_installed,
    find_equipment,
    find_equipment_by_id,
    get_install_status,
    install_equipment,
    uninstall_equipment,
)
from servers import (
    add_server,
    filter_servers_by_slots,
    find_server,
    get_free_slots,
    get_load_level,
    get_load_percent,
    sort_servers,
)
from storage import load_equipment, load_servers, save_equipment, save_servers
from utils import input_choice, input_date, input_int, input_text

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SERVERS_FILE = os.path.join(DATA_DIR, "servers.json")
EQUIPMENT_FILE = os.path.join(DATA_DIR, "equipment.json")

Action = Callable[[dict[int, dict], list[dict]], None]


def save_all(servers: dict[int, dict], equipment: list[dict]) -> None:
    """Сохранить все данные проекта в JSON-файлы."""
    save_servers(SERVERS_FILE, servers)
    save_equipment(EQUIPMENT_FILE, equipment)


def print_servers(servers: list[dict], equipment: list[dict]) -> None:
    """Вывести таблицу серверов с загрузкой."""
    if not servers:
        print("Серверы не найдены")
        return
    print(f"{'ID':>3}  {'Название':<16}{'Расположение':<14}"
          f"{'Слоты':>7}  Загрузка")
    for server in servers:
        used = count_installed(equipment, server["id"])
        load = get_load_percent(server["slots"], used)
        print(f"{server['id']:>3}  {server['name']:<16}"
              f"{server['location']:<14}{used:>3}/{server['slots']:<3}  "
              f"{load}% ({get_load_level(load)})")


def print_equipment(items: list[dict], servers: dict[int, dict]) -> None:
    """Вывести список оборудования с характеристиками."""
    if not items:
        print("Оборудование не найдено")
        return
    for item in items:
        server = servers.get(item["server_id"])
        place = server["name"] if server else "на складе"
        print(f"[{item['id']}] {item['name']} ({item['kind']}), "
              f"S/N {item['serial_number']} — {STATES[item['state']]}, "
              f"{place}")
        for characteristic in item["characteristics"]:
            print(f"      {characteristic['name']}: "
                  f"{characteristic['value']} {characteristic['unit']}")


def show_servers(servers: dict[int, dict], equipment: list[dict]) -> None:
    """Показать серверы"""
    print_servers(sort_servers(servers, reverse=True), equipment)


def search_servers(servers: dict[int, dict], equipment: list[dict]) -> None:
    """Найти сервер по названию"""
    query = input_text("Часть названия: ")
    print_servers(find_server(servers, query), equipment)


def select_servers(servers: dict[int, dict], equipment: list[dict]) -> None:
    """Отобрать серверы по количеству слотов"""
    min_slots = input_int("Минимальное количество слотов: ", min_value=1)
    print_servers(list(filter_servers_by_slots(servers, min_slots)),
                  equipment)


def create_server(servers: dict[int, dict], equipment: list[dict]) -> None:
    """Добавить сервер"""
    name = input_text("Название сервера: ")
    location = input_text("Расположение (стойка): ")
    slots = input_int("Количество слотов: ", min_value=1)
    server = add_server(servers, name, location, slots)
    save_all(servers, equipment)
    print(f"Сервер добавлен, ID {server['id']}")


def show_equipment(servers: dict[int, dict], equipment: list[dict]) -> None:
    """Показать оборудование"""
    print_equipment(equipment, servers)


def search_equipment(servers: dict[int, dict], equipment: list[dict]) -> None:
    """Найти оборудование по названию или серийному номеру"""
    query = input_text("Строка поиска: ")
    print_equipment(find_equipment(equipment, query), servers)


def create_equipment(servers: dict[int, dict], equipment: list[dict]) -> None:
    """Добавить оборудование"""
    name = input_text("Название: ")
    kind = input_text("Тип (CPU, RAM, Диск, ...): ")
    serial_number = input_text("Серийный номер: ")
    state = input_choice("Состояние: ", STATES)
    try:
        item = add_equipment(equipment, name, kind, serial_number, state)
    except ValueError as error:
        print(error)
        return
    save_all(servers, equipment)
    print(f"Оборудование добавлено, ID {item['id']}")


def create_characteristic(
    servers: dict[int, dict],
    equipment: list[dict],
) -> None:
    """Добавить характеристику оборудованию"""
    item = find_equipment_by_id(equipment, input_int("ID оборудования: "))
    if item is None:
        print("Оборудование не найдено")
        return
    name = input_text("Характеристика (например, Объем): ")
    value = input_text("Значение: ")
    unit = input("Единица измерения (можно пропустить): ").strip()
    add_characteristic(item, name, value, unit)
    save_all(servers, equipment)
    print("Характеристика сохранена")


def check_install(servers: dict[int, dict], equipment: list[dict]) -> None:
    """Проверить возможность установки в сервер"""
    server = servers.get(input_int("ID сервера: "))
    item = find_equipment_by_id(equipment, input_int("ID оборудования: "))
    if server is None or item is None:
        print("Сервер или оборудование не найдены")
        return
    used = count_installed(equipment, server["id"])
    free = get_free_slots(server["slots"], used)
    print(f"Свободных слотов в {server['name']}: {free}")
    print(f"Состояние оборудования: {STATES[item['state']]}")
    is_possible = can_install(free, item["state"])
    if item["server_id"] is not None:
        print("Оборудование уже установлено в сервер")
        is_possible = False
    print(get_install_status(is_possible))


def install(servers: dict[int, dict], equipment: list[dict]) -> None:
    """Установить оборудование в сервер"""
    equipment_id = input_int("ID оборудования: ")
    server_id = input_int("ID сервера: ")
    installed_at = input_date("Дата установки ДД.ММ.ГГГГ (Enter — сегодня): ")
    try:
        install_equipment(servers, equipment, equipment_id, server_id,
                          installed_at)
    except ValueError as error:
        print(f"{get_install_status(False)}: {error}")
        return
    save_all(servers, equipment)
    print("Оборудование установлено")


def uninstall(servers: dict[int, dict], equipment: list[dict]) -> None:
    """Снять оборудование с сервера"""
    if uninstall_equipment(equipment, input_int("ID оборудования: ")):
        save_all(servers, equipment)
        print("Оборудование снято с сервера")
    else:
        print("Оборудование не найдено или не установлено")


def update_state(servers: dict[int, dict], equipment: list[dict]) -> None:
    """Изменить состояние оборудования"""
    equipment_id = input_int("ID оборудования: ")
    state = input_choice("Новое состояние: ", STATES)
    if change_state(equipment, equipment_id, state):
        save_all(servers, equipment)
        print(f"Состояние изменено: {STATES[state]}")
    else:
        print("Оборудование не найдено")


ACTIONS: dict[str, Action] = {
    "1": show_servers,
    "2": search_servers,
    "3": select_servers,
    "4": create_server,
    "5": show_equipment,
    "6": search_equipment,
    "7": create_equipment,
    "8": create_characteristic,
    "9": check_install,
    "10": install,
    "11": uninstall,
    "12": update_state,
}


def print_menu() -> None:
    """Вывести меню, используя документацию функций-действий."""
    print("\n=== RackKeeper: учет серверного оборудования ===")
    for key, action in ACTIONS.items():
        print(f"{key}. {action.__doc__}")
    print("0. Выход")


def main() -> None:
    """Точка запуска приложения: загрузка данных и цикл меню."""
    servers = load_servers(SERVERS_FILE)
    equipment = load_equipment(EQUIPMENT_FILE)
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
        action(servers, equipment)


if __name__ == "__main__":
    main()
