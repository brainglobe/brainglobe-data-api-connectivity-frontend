from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command

from brainglobe_data_api_connectivity_frontend.connections.models import QueryResult
from brainglobe_data_api_connectivity_frontend.connections.tests.helpers import (
    create_query_result,
)


@pytest.mark.parametrize(
    ("validity_minutes", "expected_n_deleted"),
    [
        pytest.param(
            30,
            2,
            id="2 expired",
        ),
        pytest.param(
            100,
            1,
            id="1 expired",
        ),
        pytest.param(
            200,
            0,
            id="0 expired",
        ),
    ],
)
@pytest.mark.django_db
def test_cleanup_results_command(settings, validity_minutes, expected_n_deleted):
    """Test that all results older than RESULT_VALIDITY_MINUTES are deleted."""

    settings.RESULT_VALIDITY_MINUTES = validity_minutes

    # Make sure query result table is empty
    QueryResult.objects.all().delete()
    assert len(QueryResult.objects.all()) == 0

    # Add query results - one 120 minutes ago, one 60 minutes ago and one
    # at the current time
    minutes_ago = [120, 60, None]
    result_file_paths = [
        Path(create_query_result(result_file=True, minutes_ago=time).result_file.path)
        for time in minutes_ago
    ]

    out = StringIO()
    call_command("cleanup_results", stdout=out)

    # Check the expected number of results have been deleted
    assert f"Deleted {expected_n_deleted} expired results" in out.getvalue()
    assert len(QueryResult.objects.all()) == len(result_file_paths) - expected_n_deleted

    for i, result_path in enumerate(result_file_paths):
        if i < expected_n_deleted:
            assert not result_path.exists()
        else:
            assert result_path.exists()


@pytest.mark.django_db
def test_cleanup_with_missing_results_file(settings):
    """
    Test that a QueryResult with a missing result_file can be deleted
    without errors.
    """

    settings.RESULT_VALIDITY_MINUTES = 10

    # Make sure query result table is empty
    QueryResult.objects.all().delete()
    assert len(QueryResult.objects.all()) == 0

    # Add a result with no result file
    create_query_result(result_file=False, minutes_ago=20)

    out = StringIO()
    call_command("cleanup_results", stdout=out)

    # The result should have been deleted successfully
    assert "Deleted 1 expired results" in out.getvalue()
    assert len(QueryResult.objects.all()) == 0
