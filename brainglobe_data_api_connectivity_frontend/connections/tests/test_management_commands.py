from io import StringIO

import pytest
from django.core.management import call_command

from brainglobe_data_api_connectivity_frontend.connections.models import QueryResult
from brainglobe_data_api_connectivity_frontend.connections.tests.helpers import (
    create_query_result,
)


@pytest.mark.django_db
def test_cleanup_results_command(settings):

    settings.RESULT_VALIDITY_MINUTES = 10

    # Make sure query result table is empty
    QueryResult.objects.all().delete()
    assert len(QueryResult.objects.all()) == 0

    # Add new query results - 2 have expired (one with a file and one without),
    # and 1 is still valid
    expired_file_path = create_query_result(result_file=True, minutes_ago=120)
    create_query_result(result_file=False, minutes_ago=60)
    valid_file_path = create_query_result(result_file=True)

    out = StringIO()
    call_command("cleanup_results", stdout=out)

    assert "Deleted 2 expired files" in out.getvalue()
    assert len(QueryResult.objects.all()) == 1
    assert not expired_file_path.exists()
    assert valid_file_path.exists()
