from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_browse_connections_get(client):
    """Test the select line form is shown on GET"""

    response = client.get(reverse("connections:browse_connections", args=["INVALID"]))
    assert response.status_code == HTTPStatus.NOT_FOUND
