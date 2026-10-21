from http import HTTPStatus
from pathlib import Path

import polars as pl
import pytest
from django.http import Http404
from django.urls import reverse
from polars.testing import assert_frame_equal
from pytest_django.asserts import assertRaisesMessage
from pytest_django.asserts import assertRedirects
from pytest_django.asserts import assertTemplateUsed

from brainglobe_data_api_connectivity_frontend.connections.forms import BestPathForm
from brainglobe_data_api_connectivity_frontend.connections.forms import (
    DirectConnectionsForm,
)
from brainglobe_data_api_connectivity_frontend.connections.models import QueryResult
from brainglobe_data_api_connectivity_frontend.connections.tests.helpers import (
    create_query_result,
)
from brainglobe_data_api_connectivity_frontend.connections.views import (
    browse_connections,
)
from brainglobe_data_api_connectivity_frontend.connections.views import download_results
from brainglobe_data_api_connectivity_frontend.connections.views import results

pytestmark = pytest.mark.django_db


@pytest.fixture
def next_result_id():
    """Find the next available result id"""

    if QueryResult.objects.count() == 0:
        return 1

    latest_result = QueryResult.objects.latest("id")
    return latest_result.id + 1


@pytest.mark.parametrize(
    "url",
    [
        "connections:browse_connections",
        "connections:run_direct_query",
        "connections:run_path_query",
    ],
)
def test_browse_connections_invalid_sex(rf, url):
    """Test that an invalid sex routes to a 404 page."""

    sex = "INVALID"
    request = rf.get(reverse(url, args=[sex]))

    with assertRaisesMessage(Http404, "Provided sex must be one of ['male', 'female']"):
        browse_connections(request, sex=sex)


@pytest.mark.parametrize("sex", ["male", "female"])
def test_browse_connections(client, sex):
    response = client.get(reverse("connections:browse_connections", args=[sex]))

    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.context["connections_form"], DirectConnectionsForm)
    assert isinstance(response.context["path_form"], BestPathForm)
    assert response.context["sex"] == sex
    assertTemplateUsed(
        response=response, template_name="connections/browse_connections.html"
    )


@pytest.mark.parametrize(
    ("url", "sex", "form_data", "expected_result"),
    [
        pytest.param(
            "connections:run_direct_query",
            "female",
            {"region": "delta", "node_as": "ANY"},
            pl.DataFrame(
                data={
                    "region_id": ["alpha", "bravo", "echo", "bravo", "charlie"],
                    "node_as": ["input", "input", "input", "output", "output"],
                }
            ),
            id="Direct connections query - female",
        ),
        pytest.param(
            "connections:run_direct_query",
            "male",
            {"region": "juliett", "node_as": "ANY"},
            pl.DataFrame(
                data={
                    "region_id": ["hotel", "india", "kilo", "hotel"],
                    "node_as": ["input", "input", "input", "output"],
                }
            ),
            id="Direct connections query - male",
        ),
        pytest.param(
            "connections:run_path_query",
            "female",
            {
                "region0": "echo",
                "region1": "charlie",
                "strategy": "FEWEST_STEPS",
            },
            pl.DataFrame(
                data={
                    "region_id": ["echo", "bravo", "alpha", "charlie"],
                }
            ),
            id="Path query - female",
        ),
        pytest.param(
            "connections:run_path_query",
            "male",
            {
                "region0": "kilo",
                "region1": "juliett",
                "strategy": "FEWEST_STEPS",
            },
            pl.DataFrame(
                data={
                    "region_id": ["kilo", "hotel", "juliett"],
                }
            ),
            id="Path query - male",
        ),
    ],
)
def test_run_valid_query(client, url, sex, form_data, expected_result):
    """Test that running a valid query produces the correct result."""

    n_results_before = QueryResult.objects.count()
    response = client.post(reverse(url, args=[sex]), form_data)
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


@pytest.mark.parametrize(
    "url",
    [
        "connections:run_direct_query",
        "connections:run_path_query",
    ],
)
def test_run_invalid_queries(client, url):
    """
    Test that an invalid form submission creates no results and redirects
    to the search page.
    """

    n_results_before = QueryResult.objects.count()
    response = client.post(
        reverse(url, args=["male"]),
        {"INVALID_FORM_DATA": "INVALID"},
    )
    n_results_after = QueryResult.objects.count()

    # No new query results should have been created
    assert n_results_before == n_results_after

    assertRedirects(response, reverse("connections:browse_connections", args=["male"]))


def test_view_missing_result(rf, next_result_id):
    """Test that trying to view a non-existent result id throws 404"""

    request = rf.get(reverse("connections:results", args=[next_result_id]))
    with assertRaisesMessage(Http404, "No QueryResult matches the given query."):
        results(request, result_id=next_result_id)


def test_view_valid_result(client):
    """Test a valid result id is fetched and rendered on page."""

    query_result = create_query_result()
    response = client.get(reverse("connections:results", args=[query_result.id]))

    assert response.status_code == HTTPStatus.OK
    assert response.context["result"] == query_result
    assertTemplateUsed(response=response, template_name="connections/results.html")


def test_download_valid_result(client):
    """Test download of an example results file."""

    query_result = create_query_result()
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


def test_download_result_with_no_file(rf):
    """Test that trying to download a result with no file throws 404"""

    result_id = create_query_result(result_file=False).id
    request = rf.get(reverse("connections:download_results", args=[result_id]))
    with assertRaisesMessage(Http404, "File no longer available"):
        download_results(request, result_id=result_id)
