"""RackKeeper — начальный сценарий проекта (ПР1).

Проверка возможности установки нового оборудования в сервер:
сколько слотов свободно, какова загрузка сервера и можно ли
установить выбранное оборудование с учетом его состояния.
"""
from datetime import date

server_name = "srv-db-01"
server_location = "Стойка A1"
total_slots = 8
used_slots = 6

equipment_name = "Модуль памяти DDR4"
equipment_size = "32"  # объем с маркировки хранится строкой
equipment_state = "исправно"
check_date = date.today()


def get_free_slots(total: int, used: int) -> int:
    """Вернуть количество свободных слотов сервера."""
    return total - used


def get_load_percent(total: int, used: int) -> float:
    """Вернуть загрузку сервера в процентах."""
    if total == 0:
        return 100.0
    return round(used / total * 100, 1)


def get_load_level(load_percent: float) -> str:
    """Вернуть словесную оценку загрузки сервера."""
    if load_percent < 50:
        return "низкая"
    elif load_percent < 85:
        return "средняя"
    else:
        return "высокая"


def can_install(free_slots: int, state: str) -> bool:
    """Проверить, можно ли установить оборудование в сервер.

    Установка возможна, если у сервера есть свободный слот,
    а само оборудование исправно.
    """
    return free_slots > 0 and state == "исправно"


def get_install_status(is_possible: bool) -> str:
    """Вернуть текстовый статус установки оборудования."""
    if is_possible:
        return "Оборудование можно установить в сервер"
    return "Установка невозможна"


def main() -> None:
    """Выполнить сценарий проверки установки оборудования."""
    used = used_slots
    answer = input(f"Сколько слотов занято сейчас? (Enter — {used}): ")
    if answer.isdigit():
        used = int(answer)
    elif answer:
        print("Введено не число, используется значение по умолчанию")

    if used > total_slots:
        print("Занято слотов больше, чем есть в сервере, — проверьте ввод")
        used = total_slots

    free = get_free_slots(total_slots, used)
    load = get_load_percent(total_slots, used)
    size_gb = int(equipment_size)

    print()
    print(f"Сервер: {server_name} ({server_location})")
    print(f"Дата проверки: {check_date.strftime('%d.%m.%Y')}")
    print(f"Слотов всего: {total_slots}, занято: {used}, свободно: {free}")
    print(f"Загрузка: {load}% ({get_load_level(load)})")
    print(f"Оборудование: {equipment_name}, {size_gb} ГБ "
          f"({size_gb * 1024} МБ), состояние: {equipment_state}")
    print(get_install_status(can_install(free, equipment_state)))


if __name__ == "__main__":
    main()
