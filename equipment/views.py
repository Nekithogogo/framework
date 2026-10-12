from django.conf import settings
from django.http import HttpResponse
from django.utils.html import escape

from homepage.views import page
from models.equipment import find_equipment_by_id
from storage import load_inventory


def state_badge(state):
    """Подобрать цвет бейджа Bootstrap по состоянию оборудования."""
    if state.is_working:
        return "bg-success"
    if state.is_decommissioned:
        return "bg-secondary"
    return "bg-danger"


def equipment(request):
    _, _, equipment_list = load_inventory(settings.DATA_DIR)
    rows = ""
    for item in equipment_list:
        place = escape(item.server.name) if item.server else "на складе"
        rows += f"""
        <tr>
            <td>{item.id}</td>
            <td><a href="/equipment/{item.id}/">{escape(item.name)}</a></td>
            <td>{escape(item.kind)}</td>
            <td>{escape(item.serial_number)}</td>
            <td>{place}</td>
            <td>
                <span class="badge {state_badge(item.state)}">
                    {escape(item.state.name)}
                </span>
            </td>
        </tr>
        """
    content = f"""
    <h1>Оборудование</h1>
    <div class="table-responsive">
        <table class="table table-hover align-middle">
            <thead>
                <tr>
                    <th>ID</th><th>Название</th><th>Тип</th>
                    <th>Серийный номер</th><th>Сервер</th><th>Состояние</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    """
    return HttpResponse(page("RackKeeper – оборудование", content))


def equipment_detail(request, equipment_id):
    _, _, equipment_list = load_inventory(settings.DATA_DIR)
    item = find_equipment_by_id(equipment_list, equipment_id)
    if item is None:
        content = """
        <h1 class="text-danger">Оборудование не найдено</h1>
        <a href="/equipment/" class="btn btn-outline-secondary">
            ← к списку оборудования
        </a>
        """
        return HttpResponse(
            page("Оборудование не найдено", content),
            status=404,
        )

    if item.server:
        place = (f'<a href="/servers/{item.server.id}/">'
                 f"{escape(item.server.name)}</a>, установлено "
                 f"{item.installed_at.strftime('%d.%m.%Y')}")
    else:
        place = "на складе"
    rows = ""
    for characteristic in item.characteristics:
        value = f"{characteristic.value} {characteristic.unit}"
        rows += f"""
        <tr>
            <td>{escape(characteristic.name)}</td>
            <td>{escape(value)}</td>
        </tr>
        """
    if not rows:
        rows = '<tr><td colspan="2">Характеристики не указаны</td></tr>'
    installable = "да" if item.can_be_installed() else "нет"
    content = f"""
    <div class="card mb-3">
        <div class="card-body">
            <h1 class="card-title h3">{escape(item.name)}</h1>
            <p class="card-text"><strong>ID:</strong> {item.id}</p>
            <p class="card-text">
                <strong>Тип:</strong> {escape(item.kind)}
            </p>
            <p class="card-text">
                <strong>Серийный номер:</strong>
                {escape(item.serial_number)}
            </p>
            <p class="card-text"><strong>Сервер:</strong> {place}</p>
            <p class="card-text">
                <strong>Состояние:</strong>
                <span class="badge {state_badge(item.state)}">
                    {escape(item.state.name)}
                </span>
            </p>
            <p class="card-text">
                <strong>Можно установить в сервер:</strong> {installable}
            </p>
        </div>
    </div>
    <h2 class="h4">Характеристики</h2>
    <table class="table table-sm mb-3"><tbody>{rows}</tbody></table>
    <a href="/equipment/" class="btn btn-outline-secondary">
        ← к списку оборудования
    </a>
    """
    return HttpResponse(page(escape(item.name), content), status=200)
