from django.conf import settings
from django.shortcuts import render

from models.equipment import find_equipment_by_id
from storage import load_inventory


def equipment(request):
    _, _, equipment_list = load_inventory(settings.DATA_DIR)
    context = {
        "equipment": equipment_list,
    }
    return render(request, "equipment/equipment_list.html", context)


def equipment_detail(request, equipment_id):
    _, _, equipment_list = load_inventory(settings.DATA_DIR)
    item = find_equipment_by_id(equipment_list, equipment_id)
    context = {
        "item": item,
    }
    return render(
        request,
        "equipment/equipment_detail.html",
        context,
        status=404 if item is None else 200,
    )
