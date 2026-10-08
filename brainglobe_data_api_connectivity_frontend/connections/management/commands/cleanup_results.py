from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from brainglobe_data_api_connectivity_frontend.connections.models import QueryResult


class Command(BaseCommand):
    help = "Delete query results older than settings.RESULT_VALIDITY_MINUTES"

    def handle(self, *args, **options):
        deleted, _ = QueryResult.objects.expired().delete()
        self.stdout.write(f"Deleted {deleted} expired objects")

        expiry_time = timezone.now() - timedelta(
            minutes=settings.RESULT_VALIDITY_MINUTES
        )
        expired_results = QueryResult.objects.filter(created_at__lt=expiry_time)

        n_results_deleted = 0
        for result in expired_results:
            result.result_file.delete(save=True)  # delete the result file
            result.delete()  # delete the entry in the database
            n_results_deleted += 1
        self.stdout.write(f"Deleted {n_results_deleted} expired files")
