from datetime import date

import pytest

from models import Characteristic, Entity, Equipment, Server, State
from models.equipment import (
    add_equipment,
    change_equipment_state,
    count_by_server,
    count_installed,
    get_server_equipment,
    has_free_slot,
    install_equipment,
    uninstall_equipment,
)

INSTALL_DATE = date(2026, 9, 15)
WORKING = State(1, "working", "Исправно", True)
FAULTY = State(2, "faulty", "Неисправно", False)
DECOMMISSIONED = State(4, "decommissioned", "Списано", False)


def make_data() -> tuple[Server, list[Equipment]]:
    server = Server(1, "srv-web-01", "Стойка A2", 1)
    equipment: list[Equipment] = []
    add_equipment(equipment, "Kingston DDR4", "RAM", "RAM-1", WORKING)
    add_equipment(equipment, "Kingston DDR4", "RAM", "RAM-2", WORKING)
    return server, equipment


def test_equipment_creation():
    item = Equipment(1, "Samsung PM893", "SSD", "SSD-1", WORKING)
    assert item.id == 1
    assert item.state is WORKING
    assert item.server is None
    assert not item.is_installed
    assert item.characteristics == []
    assert str(item) == ("[1] Samsung PM893 (SSD), S/N SSD-1 — Исправно, "
                         "на складе")


def test_duplicate_serial_number_forbidden():
    _, equipment = make_data()
    with pytest.raises(ValueError):
        add_equipment(equipment, "Другой модуль", "RAM", "RAM-1", WORKING)


def test_characteristics():
    item = Equipment(1, "Kingston DDR4", "RAM", "RAM-1", WORKING)
    item.add_characteristic(Characteristic("Объем", "16", "ГБ"))
    item.add_characteristic(Characteristic("объем", "32", "ГБ"))
    assert len(item.characteristics) == 1
    assert str(item.get_characteristic("ОБЪЕМ")) == "объем: 32 ГБ"


def test_install_links_objects():
    server, equipment = make_data()
    install_equipment(equipment, equipment[0], server, INSTALL_DATE)
    assert equipment[0].server is server
    assert equipment[0].installed_at == INSTALL_DATE
    assert get_server_equipment(equipment, server) == [equipment[0]]
    assert count_by_server(equipment) == {1: 1}


def test_install_into_full_server_forbidden():
    server, equipment = make_data()
    install_equipment(equipment, equipment[0], server, INSTALL_DATE)
    assert not has_free_slot(equipment, server)
    with pytest.raises(ValueError):
        install_equipment(equipment, equipment[1], server, INSTALL_DATE)


def test_install_faulty_equipment_forbidden():
    server, equipment = make_data()
    equipment[0].change_state(FAULTY)
    with pytest.raises(ValueError):
        install_equipment(equipment, equipment[0], server, INSTALL_DATE)
    assert not equipment[0].is_installed


def test_uninstall_frees_slot():
    server, equipment = make_data()
    install_equipment(equipment, equipment[0], server, INSTALL_DATE)
    assert uninstall_equipment(equipment, 1)
    assert count_installed(equipment, server) == 0
    install_equipment(equipment, equipment[1], server, INSTALL_DATE)
    assert not uninstall_equipment(equipment, 1)


def test_decommission_uninstalls_equipment():
    server, equipment = make_data()
    install_equipment(equipment, equipment[0], server, INSTALL_DATE)
    assert change_equipment_state(equipment, 1, DECOMMISSIONED)
    assert equipment[0].server is None
    assert not change_equipment_state(equipment, 99, WORKING)


def test_to_dict_stores_ids_instead_of_objects():
    server, equipment = make_data()
    install_equipment(equipment, equipment[0], server, INSTALL_DATE)
    data = equipment[0].to_dict()
    assert data["server_id"] == 1
    assert data["state_id"] == 1
    assert data["installed_at"] == "2026-09-15"


def test_entity_polymorphism():
    server, equipment = make_data()
    objects: list[Entity] = [server, WORKING, equipment[0]]
    assert [item.to_dict()["id"] for item in objects] == [1, 1, 1]
    with pytest.raises(NotImplementedError):
        Entity(1).to_dict()
