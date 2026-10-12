import pytest

from models import Server
from models.servers import (
    add_server,
    check_server_slots,
    filter_servers_by_slots,
    find_server,
    find_server_by_id,
    sort_servers,
)


def make_servers() -> list[Server]:
    servers: list[Server] = []
    add_server(servers, "srv-db-01", "Стойка A1", 8)
    add_server(servers, "srv-web-01", "Стойка A2", 4)
    return servers


def test_server_creation():
    server = Server(1, "srv-db-01", "Стойка A1", 8)
    assert server.id == 1
    assert server.name == "srv-db-01"
    assert server.location == "Стойка A1"
    assert server.slots == 8
    assert str(server) == "srv-db-01 (Стойка A1, слотов: 8)"


def test_server_slots_are_validated():
    with pytest.raises(ValueError):
        Server(1, "srv-bad", "Стойка C1", 0)
    server = Server(1, "srv", "A1", 4)
    with pytest.raises(ValueError):
        server.slots = -1
    assert Server.validate_slots(2)
    assert not Server.validate_slots(0)


def test_server_is_suitable_for():
    server = Server(1, "srv-db-01", "Стойка A1", 8)
    assert server.is_suitable_for(8)
    assert not server.is_suitable_for(9)


def test_free_slots_and_load():
    server = Server(1, "srv-db-01", "Стойка A1", 8)
    assert server.get_free_slots(6) == 2
    assert server.get_free_slots(10) == 0
    assert server.get_load_percent(6) == 75.0
    assert Server.get_load_level(75.0) == "средняя"


def test_server_from_data_and_to_dict():
    data = {"id": 3, "name": "srv", "location": "B1", "slots": 12}
    assert Server.from_data(data).to_dict() == data


def test_add_server_returns_object():
    servers = make_servers()
    assert len(servers) == 2
    assert isinstance(servers[1], Server)
    assert servers[1].id == 2


def test_find_server():
    servers = make_servers()
    assert find_server(servers, "DB") == [servers[0]]
    assert find_server_by_id(servers, 2) is servers[1]
    assert find_server_by_id(servers, 99) is None


def test_check_filter_and_sort_servers():
    servers = make_servers()
    assert check_server_slots(servers, 1, 8)
    assert not check_server_slots(servers, 2, 8)
    assert list(filter_servers_by_slots(servers, 5)) == [servers[0]]
    assert sort_servers(servers) == [servers[1], servers[0]]
