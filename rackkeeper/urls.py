"""Корневая маршрутизация проекта RackKeeper."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("servers/", include("servers.urls")),
    path("equipment/", include("equipment.urls")),
]

handler404 = "homepage.views.page_not_found"
