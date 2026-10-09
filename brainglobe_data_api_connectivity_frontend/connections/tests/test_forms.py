import pytest

from brainglobe_data_api_connectivity_frontend.connections.forms import (
    DirectConnectionsForm,
)


@pytest.mark.parametrize(
    ("sex", "expected_nodes"),
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
def test_direct_connections_form(sex, expected_nodes):
    """Test choices are correctly populated from graph."""

    form = DirectConnectionsForm(sex=sex)
    field_choices = {}
    for name, field in form.fields.items():
        field_choices[name] = dict(field.choices)

    expected_nodes_with_blank = expected_nodes.copy()
    expected_nodes_with_blank[""] = "------"

    assert field_choices["node0"] == expected_nodes
    assert field_choices["node1"] == expected_nodes_with_blank
    assert field_choices["connections_lookup"] == {"ALL": "ALL", "REPORTED": "REPORTED"}
    assert field_choices["node0_as"] == {
        "ANY": "ANY",
        "OUTPUT": "OUTPUT",
        "INPUT": "INPUT",
    }
