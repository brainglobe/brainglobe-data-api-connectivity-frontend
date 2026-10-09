from http import HTTPStatus
from pathlib import Path

import polars as pl
import pytest
from django.core.files.base import ContentFile
from django.http import Http404
from django.urls import reverse
from polars.testing import assert_frame_equal
from pytest_django.asserts import assertRaisesMessage
from pytest_django.asserts import assertRedirects
from pytest_django.asserts import assertTemplateUsed

from brainglobe_data_api_connectivity_frontend.connections.forms import (
    DirectConnectionsForm,
)
from brainglobe_data_api_connectivity_frontend.connections.models import QueryResult
from brainglobe_data_api_connectivity_frontend.connections.views import (
    browse_connections,
)
from brainglobe_data_api_connectivity_frontend.connections.views import download_results
from brainglobe_data_api_connectivity_frontend.connections.views import results

pytestmark = pytest.mark.django_db


@pytest.fixture
def query_result_no_file():
    """Add a new QueryResult to the database with no result_file"""

    new_result = QueryResult(sex="female", n_rows=876)
    new_result.save()

    return new_result


@pytest.fixture
def query_result(query_result_no_file):
    """Add a new QueryResult to the database including a result_file"""

    query_result_no_file.result_file.save(
        name="test", content=ContentFile("hello world")
    )
    return query_result_no_file


@pytest.fixture
def next_result_id():
    """Find the next available result id"""

    if QueryResult.objects.count() == 0:
        return 1

    latest_result = QueryResult.objects.latest("id")
    return latest_result.id + 1


def test_browse_connections_invalid_sex(rf):
    """Test that an invalid sex routes to a 404 page."""

    sex = "INVALID"
    request = rf.get(reverse("connections:browse_connections", args=[sex]))

    with assertRaisesMessage(Http404, "Provided sex must be one of ['male', 'female']"):
        browse_connections(request, sex=sex)


@pytest.mark.parametrize("sex", ["male", "female"])
def test_browse_connections_get(client, sex):
    response = client.get(reverse("connections:browse_connections", args=[sex]))

    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.context["form"], DirectConnectionsForm)
    assert response.context["sex"] == sex
    assertTemplateUsed(
        response=response, template_name="connections/browse_connections.html"
    )


@pytest.mark.parametrize(
    ("sex", "region_id", "expected_result"),
    [
        pytest.param(
            "female",
            "delta",
            pl.DataFrame(
                data={
                    "region_id": ["alpha", "bravo", "echo", "bravo", "charlie"],
                    "node_as": ["input", "input", "input", "output", "output"],
                }
            ),
            id="female",
        ),
        pytest.param(
            "male",
            "juliett",
            pl.DataFrame(
                data={
                    "region_id": ["hotel", "india", "kilo", "hotel"],
                    "node_as": ["input", "input", "input", "output"],
                }
            ),
            id="male",
        ),
    ],
)
def test_browse_connections_post(client, sex, region_id, expected_result):

    n_results_before = QueryResult.objects.count()
    response = client.post(
        reverse("connections:browse_connections", args=[sex]),
        {"region": region_id, "node_as": "ANY"},
    )
    n_results_after = QueryResult.objects.count()

    latest_result = QueryResult.objects.latest("id")

    # Check one result was produced with correct metadata and csv file
    assert n_results_after == n_results_before + 1
    assert latest_result.n_rows == len(expected_result)
    assert latest_result.sex == sex

    result_file_path = Path(latest_result.result_file.path)
    assert result_file_path.exists()
    assert result_file_path.suffix == ".csv"

    result_df = pl.read_csv(result_file_path)
    assert_frame_equal(result_df, expected_result)

    # The view should redirect to the results page on successful query
    assertRedirects(response, reverse("connections:results", args=[latest_result.id]))


def test_view_missing_result(rf, next_result_id):
    """Test that trying to view a non-existent result id throws 404"""

    request = rf.get(reverse("connections:results", args=[next_result_id]))
    with assertRaisesMessage(Http404, "No QueryResult matches the given query."):
        results(request, result_id=next_result_id)


def test_view_valid_result(client, query_result):
    """Test a valid result id is fetched and rendered on page."""

    response = client.get(reverse("connections:results", args=[query_result.id]))
    assert response.status_code == HTTPStatus.OK
    assert response.context["result"] == query_result
    assertTemplateUsed(response=response, template_name="connections/results.html")


def test_download_valid_result(client, query_result):
    """Test download of an example results file."""

    response = client.get(
        reverse("connections:download_results", args=[query_result.id])
    )
    assert response.status_code == HTTPStatus.OK
    assert b"".join(response.streaming_content) == b"hello world"
    assert response["Content-Disposition"] == 'attachment; filename="test"'


def test_download_missing_result(rf, next_result_id):
    """Test that trying to download a non-existent result id throws 404"""

    request = rf.get(reverse("connections:download_results", args=[next_result_id]))
    with assertRaisesMessage(Http404, "No QueryResult matches the given query."):
        download_results(request, result_id=next_result_id)


def test_download_result_with_no_file(rf, query_result_no_file):
    """Test that trying to download a result with no file throws 404"""

    result_id = query_result_no_file.id
    request = rf.get(reverse("connections:download_results", args=[result_id]))
    with assertRaisesMessage(Http404, "File no longer available"):
        download_results(request, result_id=result_id)
