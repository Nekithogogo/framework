"""Проверка маршрутов и страниц Django-приложения."""
import os

import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rackkeeper.settings")
django.setup()

from django.test import Client, override_settings  # noqa: E402


@pytest.fixture
def client() -> Client:
    return Client(HTTP_HOST="localhost")


@pytest.mark.parametrize("url", [
    "/",
    "/servers/",
    "/servers/1/",
    "/equipment/",
    "/equipment/1/",
])
def test_pages_open(client, url):
    assert client.get(url).status_code == 200


@pytest.mark.parametrize("url, text", [
    ("/servers/999/", "Сервер не найден"),
    ("/equipment/999/", "Оборудование не найдено"),
])
def test_missing_objects_return_404(client, url, text):
    response = client.get(url)
    assert response.status_code == 404
    assert text in response.content.decode()


def test_server_page_shows_installed_equipment(client):
    content = client.get("/servers/1/").content.decode()
    assert "srv-db-01" in content
    assert "Intel Xeon Silver 4314" in content


def test_equipment_page_shows_characteristics(client):
    content = client.get("/equipment/2/").content.decode()
    assert "Объем" in content
    assert "32 ГБ" in content


def test_custom_404_page(client):
    with override_settings(DEBUG=False):
        response = client.get("/nonexistent/")
    assert response.status_code == 404
    assert "страница не найдена" in response.content.decode()
