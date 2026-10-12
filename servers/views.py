from django.conf import settings
from django.shortcuts import render

from models import Server
from models.equipment import count_by_server, get_server_equipment
from models.servers import find_server_by_id, sort_servers
from storage import load_inventory


def make_server_row(server, used):
    """Подготовить данные сервера и его загрузки для шаблона."""
    load = server.get_load_percent(used)
    return {
        "server": server,
        "used": used,
        "free": server.get_free_slots(used),
        "load": load,
        "level": Server.get_load_level(load),
    }


def servers(request):
    servers_list, _, equipment_list = load_inventory(settings.DATA_DIR)
    used_slots = count_by_server(equipment_list)
    context = {
        "server_rows": [
            make_server_row(server, used_slots.get(server.id, 0))
            for server in sort_servers(servers_list, reverse=True)
        ],
    }
    return render(request, "servers/server_list.html", context)


def server_detail(request, server_id):
    servers_list, _, equipment_list = load_inventory(settings.DATA_DIR)
    server = find_server_by_id(servers_list, server_id)
    context = {"server": server}
    if server is not None:
        installed = get_server_equipment(equipment_list, server)
        context["row"] = make_server_row(server, len(installed))
        context["installed"] = installed
    return render(
        request,
        "servers/server_detail.html",
        context,
        status=404 if server is None else 200,
    )
