from django.core.management.base import BaseCommand

from brainglobe_data_api_connectivity_frontend.connections.graph_data import Sex
from brainglobe_data_api_connectivity_frontend.connections.graph_data import (
    get_connections,
)


class Command(BaseCommand):
    help = "Make sure neurome datasets (CSV) are downloaded to the server."

    def handle(self, *args, **options):
        get_connections(Sex.MALE)
        get_connections(Sex.FEMALE)
        self.stdout.write("Fetched male and female datasets.")
