from django.urls import path

from . import views

app_name = "servers"

urlpatterns = [
    path("", views.servers, name="list"),
    path("<int:server_id>/", views.server_detail, name="detail"),
]
