from django.urls import path

from . import views

app_name = "connections"
urlpatterns = [
    path("", views.browse_connections, name="browse_connections"),
]
