from datetime import date

import pytest

from equipment import (
    add_characteristic,
    add_equipment,
    change_state,
    count_installed,
    has_free_slot,
    install_equipment,
    uninstall_equipment,
)
from servers import add_server

INSTALL_DATE = date(2026, 9, 15)


def make_data() -> tuple[dict[int, dict], list[dict]]:
    servers: dict[int, dict] = {}
    add_server(servers, "srv-web-01", "Стойка A2", 1)
    equipment: list[dict] = []
    add_equipment(equipment, "Kingston DDR4", "RAM", "RAM-1")
    add_equipment(equipment, "Kingston DDR4", "RAM", "RAM-2")
    return servers, equipment


def test_add_equipment():
    _, equipment = make_data()
    assert len(equipment) == 2
    assert equipment[1]["id"] == 2
    assert equipment[0]["server_id"] is None


def test_duplicate_serial_number_forbidden():
    _, equipment = make_data()
    with pytest.raises(ValueError):
        add_equipment(equipment, "Другой модуль", "RAM", "RAM-1")


def test_add_characteristic_replaces_value():
    _, equipment = make_data()
    add_characteristic(equipment[0], "Объем", "16", "ГБ")
    add_characteristic(equipment[0], "объем", "32", "ГБ")
    assert equipment[0]["characteristics"] == [
        {"name": "Объем", "value": "32", "unit": "ГБ"}
    ]


def test_install_equipment():
    servers, equipment = make_data()
    install_equipment(servers, equipment, 1, 1, INSTALL_DATE)
    assert equipment[0]["server_id"] == 1
    assert equipment[0]["installed_at"] == "2026-09-15"
    assert count_installed(equipment, 1) == 1


def test_install_into_full_server_forbidden():
    servers, equipment = make_data()
    install_equipment(servers, equipment, 1, 1, INSTALL_DATE)
    assert not has_free_slot(servers, equipment, 1)
    with pytest.raises(ValueError):
        install_equipment(servers, equipment, 2, 1, INSTALL_DATE)


def test_install_faulty_equipment_forbidden():
    servers, equipment = make_data()
    change_state(equipment, 1, "faulty")
    with pytest.raises(ValueError):
        install_equipment(servers, equipment, 1, 1, INSTALL_DATE)


def test_uninstall_frees_slot():
    servers, equipment = make_data()
    install_equipment(servers, equipment, 1, 1, INSTALL_DATE)
    assert uninstall_equipment(equipment, 1)
    assert has_free_slot(servers, equipment, 1)
    assert not uninstall_equipment(equipment, 1)


def test_decommission_uninstalls_equipment():
    servers, equipment = make_data()
    install_equipment(servers, equipment, 1, 1, INSTALL_DATE)
    assert change_state(equipment, 1, "decommissioned")
    assert equipment[0]["server_id"] is None
