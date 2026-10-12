from django.conf import settings
from django.shortcuts import render

from storage import load_inventory


def index(request):
    servers, _, equipment = load_inventory(settings.DATA_DIR)
    context = {
        "servers": servers,
        "equipment": equipment,
        "installed_count": sum(1 for item in equipment if item.is_installed),
        "attention": [item for item in equipment if item.needs_attention],
    }
    return render(request, "homepage/index.html", context)


def page_not_found(request, exception):
    return render(request, "homepage/404.html", status=404)
