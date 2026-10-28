from django.urls import path

from . import views

app_name = "connections"
urlpatterns = [
    path("<str:sex>", views.browse_connections, name="browse_connections"),
    path(
        "run_direct_connections_query/<str:sex>",
        views.run_direct_connections_query,
        name="run_direct_query",
    ),
    path(
        "run_direct_connections_between_query/<str:sex>",
        views.run_direct_connections_between_query,
        name="run_direct_between_query",
    ),
    path(
        "run_bidirectional_connections_query/<str:sex>",
        views.run_bidirectional_connections_query,
        name="run_bidirectional_query",
    ),
    path("run_path_query/<str:sex>", views.run_path_query, name="run_path_query"),
    path("results/<int:result_id>/", views.results, name="results"),
    path(
        "results/<int:result_id>/download/",
        views.download_results,
        name="download_results",
    ),
]
