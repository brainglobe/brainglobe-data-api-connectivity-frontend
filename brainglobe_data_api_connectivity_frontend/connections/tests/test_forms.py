import pytest

from brainglobe_data_api_connectivity_frontend.connections.forms import (
    DirectConnectionsForm,
)


@pytest.mark.parametrize(
    ("sex", "expected_choices"),
    [
        pytest.param(
            "female",
            {
                "alpha": "alpha",
                "bravo": "bravo",
                "charlie": "charlie",
                "delta": "delta",
                "echo": "echo",
            },
            id="female",
        ),
        pytest.param(
            "male",
            {"hotel": "hotel", "india": "india", "juliett": "juliett", "kilo": "kilo"},
            id="male",
        ),
    ],
)
def test_direct_connections_form(sex, expected_choices):
    """Test choices are correctly populated from graph."""

    form = DirectConnectionsForm(sex=sex)
    region_choices = dict(form.fields["region"].choices)
    node_as_choices = dict(form.fields["node_as"].choices)

    assert region_choices == expected_choices
    assert node_as_choices == {"ANY": "ANY", "OUTPUT": "OUTPUT", "INPUT": "INPUT"}
