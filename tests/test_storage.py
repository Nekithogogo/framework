from storage import load_servers, read_json, save_servers


def test_servers_roundtrip(tmp_path):
    filename = str(tmp_path / "servers.json")
    servers = {1: {"id": 1, "name": "srv", "location": "A1", "slots": 4}}
    save_servers(filename, servers)
    assert load_servers(filename) == servers


def test_missing_file_gives_empty_list(tmp_path):
    assert read_json(str(tmp_path / "missing.json")) == []


def test_broken_file_gives_empty_list(tmp_path):
    filename = tmp_path / "broken.json"
    filename.write_text("[{", encoding="utf-8")
    assert read_json(str(filename)) == []
