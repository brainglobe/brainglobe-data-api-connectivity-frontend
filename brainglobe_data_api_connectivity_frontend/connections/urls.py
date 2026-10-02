from django.urls import path

from . import views

app_name = "connections"
urlpatterns = [
    path("", views.browse_connections, name="browse_connections"),
    path("results/<int:result_id>/", views.results, name="results"),
    path(
        "results/<int:result_id>/download/",
        views.download_results,
        name="download_results",
    ),
]
