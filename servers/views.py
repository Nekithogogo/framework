from django.conf import settings
from django.http import HttpResponse
from django.utils.html import escape

from homepage.views import page
from models import Server
from models.equipment import count_by_server, get_server_equipment
from models.servers import find_server_by_id, sort_servers
from storage import load_inventory


def load_badge(load_percent):
    """Подобрать цвет бейджа Bootstrap по загрузке сервера."""
    level = Server.get_load_level(load_percent)
    return {"низкая": "bg-success", "средняя": "bg-warning"}.get(
        level, "bg-danger"
    )


def servers(request):
    servers_list, _, equipment_list = load_inventory(settings.DATA_DIR)
    used_slots = count_by_server(equipment_list)
    items = ""
    for server in sort_servers(servers_list, reverse=True):
        used = used_slots.get(server.id, 0)
        load = server.get_load_percent(used)
        items += f"""
        <a href="/servers/{server.id}/"
           class="list-group-item list-group-item-action
                  d-flex justify-content-between align-items-center">
            <span>
                <strong>{escape(server.name)}</strong>
                <small class="text-muted">{escape(server.location)}</small>
            </span>
            <span class="badge {load_badge(load)}">
                занято {used} из {server.slots}
            </span>
        </a>
        """
    content = f"""
    <h1>Серверы</h1>
    <div class="list-group">{items}</div>
    """
    return HttpResponse(page("RackKeeper – серверы", content))


def server_detail(request, server_id):
    servers_list, _, equipment_list = load_inventory(settings.DATA_DIR)
    server = find_server_by_id(servers_list, server_id)
    if server is None:
        content = """
        <h1 class="text-danger">Сервер не найден</h1>
        <a href="/servers/" class="btn btn-outline-secondary">
            ← к списку серверов
        </a>
        """
        return HttpResponse(page("Сервер не найден", content), status=404)

    installed = get_server_equipment(equipment_list, server)
    free = server.get_free_slots(len(installed))
    load = server.get_load_percent(len(installed))
    status = "есть свободные слоты" if free else "свободных слотов нет"
    badge = "bg-success" if free else "bg-danger"
    rows = ""
    for item in installed:
        rows += f"""
        <li class="list-group-item">
            <a href="/equipment/{item.id}/">{escape(item.name)}</a>
            ({escape(item.kind)}) — {escape(item.state.name)}
        </li>
        """
    if not rows:
        rows = '<li class="list-group-item">Оборудование не установлено</li>'
    content = f"""
    <div class="card mb-3">
        <div class="card-body">
            <h1 class="card-title h3">{escape(server.name)}</h1>
            <p class="card-text"><strong>ID:</strong> {server.id}</p>
            <p class="card-text">
                <strong>Расположение:</strong> {escape(server.location)}
            </p>
            <p class="card-text">
                <strong>Слоты:</strong> {server.slots},
                занято {len(installed)}, свободно {free}
            </p>
            <p class="card-text">
                <strong>Загрузка:</strong> {load}%
                ({Server.get_load_level(load)})
                <span class="badge {badge}">{status}</span>
            </p>
        </div>
    </div>
    <h2 class="h4">Установленное оборудование</h2>
    <ul class="list-group mb-3">{rows}</ul>
    <a href="/servers/" class="btn btn-outline-secondary">
        ← к списку серверов
    </a>
    """
    return HttpResponse(page(escape(server.name), content), status=200)
