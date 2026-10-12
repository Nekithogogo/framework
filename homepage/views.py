from django.conf import settings
from django.http import HttpResponse

from storage import load_inventory


def page(title, content):
    """Собрать HTML-документ с общим каркасом всех страниц проекта."""
    bootstrap = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
        "/dist/css/bootstrap.min.css"
    )
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <link rel="stylesheet" href="{bootstrap}">
</head>
<body>
    <nav class="nav bg-dark mb-4 px-3">
        <a class="nav-link text-white fw-bold" href="/">RackKeeper</a>
        <a class="nav-link text-white-50" href="/servers/">Серверы</a>
        <a class="nav-link text-white-50" href="/equipment/">Оборудование</a>
    </nav>
    <main class="container">{content}</main>
</body>
</html>"""


def index(request):
    servers, _, equipment = load_inventory(settings.DATA_DIR)
    installed = sum(1 for item in equipment if item.is_installed)
    attention = sum(
        1 for item in equipment
        if not item.state.is_working and not item.state.is_decommissioned
    )
    content = f"""
    <h1 class="display-5">RackKeeper</h1>
    <p class="lead">Система учета серверного оборудования.</p>
    <p>
        Учет серверов, установленного в них оборудования,
        его характеристик и состояния.
    </p>
    <ul class="list-group mb-4">
        <li class="list-group-item">Серверов: {len(servers)}</li>
        <li class="list-group-item">
            Единиц оборудования: {len(equipment)},
            из них установлено в серверы: {installed}
        </li>
        <li class="list-group-item">Требуют внимания: {attention}</li>
    </ul>
    <p>Основные разделы:</p>
    <a href="/servers/" class="btn btn-primary me-2">Серверы</a>
    <a href="/equipment/" class="btn btn-secondary">Оборудование</a>
    """
    return HttpResponse(page("RackKeeper", content))


def page_not_found(request, exception):
    content = """
    <h1 class="text-danger">404 – страница не найдена</h1>
    <p>Проверьте адрес или вернитесь на главную.</p>
    <a href="/" class="btn btn-primary">На главную</a>
    """
    return HttpResponse(
        page("404 – страница не найдена", content),
        status=404,
    )
