from django.apps import AppConfig
from django.conf import settings

from brainglobe_data_api_connectivity_frontend.connections.graph_data import Sex
from brainglobe_data_api_connectivity_frontend.connections.graph_data import (
    get_connections,
)


class ConnectionsConfig(AppConfig):
    name = "brainglobe_data_api_connectivity_frontend.connections"

    def ready(self) -> None:
        """
        Cache the male and female connections on startup.
        """

        if settings.CACHE_ON_STARTUP:
            get_connections(Sex.MALE)
            get_connections(Sex.FEMALE)
