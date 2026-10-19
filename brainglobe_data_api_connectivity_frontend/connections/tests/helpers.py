from datetime import timedelta

from django.core.files.base import ContentFile
from django.utils import timezone

from brainglobe_data_api_connectivity_frontend.connections.models import QueryResult


def create_query_result(
    *,
    minutes_ago: int | None = None,
    result_file: bool = True,
) -> QueryResult:
    """Create a new QueryResult in the database.

    Parameters
    ----------
    minutes_ago : int | None, optional
        If provided, overwrite the default created_at value (normally the
        current time) with current time - minutes_ago.
    result_file : bool, optional
        Whether to include a results file.

    Returns
    -------
    QueryResult
        The created QueryResult
    """

    result = QueryResult(sex="female", n_rows=876)
    if result_file:
        result.result_file.save(name="test", content=ContentFile("hello world"))

    result.save()  # Automatically sets created_at as the current time

    if minutes_ago is not None:
        # Overwrite the default created_at time
        result.created_at = timezone.now() - timedelta(minutes=minutes_ago)
        result.save()

    return result
