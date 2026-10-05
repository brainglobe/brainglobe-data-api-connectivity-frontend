from http import HTTPStatus
from pathlib import Path

import polars as pl
import pytest
from django.urls import reverse
from polars.testing import assert_frame_equal
from pytest_django.asserts import assertRedirects
from pytest_django.asserts import assertTemplateUsed

from brainglobe_data_api_connectivity_frontend.connections.forms import (
    DirectConnectionsForm,
)
from brainglobe_data_api_connectivity_frontend.connections.models import QueryResult


@pytest.mark.django_db
def test_browse_connections_invalid_sex(client):
    """Test that an invalid sex routes to a 404 page."""

    response = client.get(reverse("connections:browse_connections", args=["INVALID"]))
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize("sex", ["male", "female"])
@pytest.mark.django_db
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
        (
            "female",
            "delta",
            pl.DataFrame(
                data={
                    "region_id": ["alpha", "bravo", "echo", "bravo", "charlie"],
                    "node_as": ["input", "input", "input", "output", "output"],
                }
            ),
        ),
        (
            "male",
            "juliett",
            pl.DataFrame(
                data={
                    "region_id": ["hotel", "india", "kilo", "hotel"],
                    "node_as": ["input", "input", "input", "output"],
                }
            ),
        ),
    ],
)
@pytest.mark.django_db
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
