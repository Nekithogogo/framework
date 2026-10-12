import pytest

from servers import (
    add_server,
    check_server_slots,
    filter_servers_by_slots,
    find_server,
    get_free_slots,
    get_load_percent,
    sort_servers,
)


def make_servers() -> dict[int, dict]:
    servers: dict[int, dict] = {}
    add_server(servers, "srv-db-01", "Стойка A1", 8)
    add_server(servers, "srv-web-01", "Стойка A2", 4)
    return servers


def test_add_server():
    servers = make_servers()
    assert len(servers) == 2
    assert servers[2]["name"] == "srv-web-01"


def test_add_server_with_zero_slots_forbidden():
    with pytest.raises(ValueError):
        add_server({}, "srv-bad", "Стойка C1", 0)


def test_find_server_ignores_case():
    assert find_server(make_servers(), "DB")[0]["id"] == 1


def test_check_server_slots():
    servers = make_servers()
    assert check_server_slots(servers, 1, 8)
    assert not check_server_slots(servers, 2, 8)
    assert not check_server_slots(servers, 99, 1)


def test_filter_and_sort_servers():
    servers = make_servers()
    assert [s["id"] for s in filter_servers_by_slots(servers, 5)] == [1]
    assert [s["id"] for s in sort_servers(servers)] == [2, 1]


def test_free_slots_and_load():
    assert get_free_slots(8, 6) == 2
    assert get_free_slots(4, 5) == 0
    assert get_load_percent(8, 6) == 75.0
