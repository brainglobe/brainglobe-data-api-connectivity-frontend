import pytest

from brainglobe_data_api_connectivity_frontend.connections.forms import BestPathForm
from brainglobe_data_api_connectivity_frontend.connections.forms import (
    DirectConnectionsForm,
)

FEMALE_REGIONS = {
    "alpha": "alpha",
    "bravo": "bravo",
    "charlie": "charlie",
    "delta": "delta",
    "echo": "echo",
}
MALE_REGIONS = {
    "hotel": "hotel",
    "india": "india",
    "juliett": "juliett",
    "kilo": "kilo",
}


@pytest.mark.parametrize(
    ("sex", "expected_choices"),
    [
        pytest.param(
            "female",
            FEMALE_REGIONS,
            id="female",
        ),
        pytest.param(
            "male",
            MALE_REGIONS,
            id="male",
        ),
    ],
)
def test_direct_connections_form(sex, expected_choices):
    """Test choices are correctly populated from graph."""

    form = DirectConnectionsForm(sex=sex)
    region_choices = dict(form.fields["region"].choices)  # type: ignore[attr-defined]
    node_as_choices = dict(form.fields["node_as"].choices)  # type: ignore[attr-defined]

    assert region_choices == expected_choices
    assert node_as_choices == {"ANY": "ANY", "OUTPUT": "OUTPUT", "INPUT": "INPUT"}


@pytest.mark.parametrize(
    ("sex", "expected_choices"),
    [
        pytest.param(
            "female",
            FEMALE_REGIONS,
            id="female",
        ),
        pytest.param(
            "male",
            MALE_REGIONS,
            id="male",
        ),
    ],
)
def test_best_path_form(sex, expected_choices):
    """Test choices are correctly populated from graph."""

    form = BestPathForm(sex=sex)
    source_region_choices = dict(form.fields["region0"].choices)
    target_region_choices = dict(form.fields["region1"].choices)
    strategy_choices = dict(form.fields["strategy"].choices)

    assert source_region_choices == expected_choices
    assert target_region_choices == expected_choices
    assert strategy_choices == {
        "FEWEST_STEPS": "Fewest Steps",
        "WEAKEST_TOTAL_WEIGHT": "Weakest Total Weight",
        "WIDEST_PATH": "Widest Path",
    }
