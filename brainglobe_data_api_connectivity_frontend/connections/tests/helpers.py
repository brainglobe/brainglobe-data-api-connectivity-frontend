from datetime import timedelta
from pathlib import Path

from django.core.files.base import ContentFile
from django.utils import timezone

from brainglobe_data_api_connectivity_frontend.connections.models import QueryResult


def create_query_result(
    minutes_ago: int | None = None,
    *,
    result_file: bool = True,
) -> Path | None:

    result = QueryResult(sex="female", n_rows=876)
    if result_file:
        result.result_file.save(name="test", content=ContentFile("hello world"))

    result.save()  # Automatically sets created_at as the current time

    if minutes_ago is not None:
        # Overwrite the default created_at time
        result.created_at = timezone.now() - timedelta(minutes=minutes_ago)
        result.save()

    if result.result_file:
        return Path(result.result_file.path)
    return None
