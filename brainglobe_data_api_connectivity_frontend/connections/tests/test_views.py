from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from brainglobe_data_api_connectivity_frontend.connections.forms import (
    DirectConnectionsForm,
)


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
