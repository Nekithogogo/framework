import json

from models import Server, State
from storage import (
    load_equipment,
    load_servers,
    read_json,
    save_equipment,
    save_servers,
)

STATES = [State(1, "working", "Исправно", True)]


def write(path, data) -> str:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return str(path)


def test_servers_roundtrip(tmp_path):
    filename = str(tmp_path / "servers.json")
    save_servers(filename, [Server(1, "srv", "A1", 4)])
    servers = load_servers(filename)
    assert isinstance(servers[0], Server)
    assert servers[0].to_dict() == {
        "id": 1, "name": "srv", "location": "A1", "slots": 4,
    }


def test_load_equipment_restores_links(tmp_path):
    servers = [Server(1, "srv", "A1", 4)]
    filename = write(tmp_path / "equipment.json", [{
        "id": 1, "name": "DDR4", "kind": "RAM", "serial_number": "R-1",
        "server_id": 1, "installed_at": "2026-09-01", "state_id": 1,
        "characteristics": [{"name": "Объем", "value": "32", "unit": "ГБ"}],
    }])
    item = load_equipment(filename, servers, STATES)[0]
    assert item.server is servers[0]
    assert item.state is STATES[0]
    assert str(item.characteristics[0]) == "Объем: 32 ГБ"

    save_equipment(filename, [item])
    assert read_json(filename)[0]["server_id"] == 1


def test_equipment_with_unknown_server_is_skipped(tmp_path):
    filename = write(tmp_path / "equipment.json", [{
        "id": 1, "name": "DDR4", "kind": "RAM", "serial_number": "R-1",
        "server_id": 42, "state_id": 1,
    }])
    assert load_equipment(filename, [], STATES) == []


def test_missing_and_broken_files(tmp_path):
    assert read_json(str(tmp_path / "missing.json")) == []
    broken = tmp_path / "broken.json"
    broken.write_text("[{", encoding="utf-8")
    assert read_json(str(broken)) == []
