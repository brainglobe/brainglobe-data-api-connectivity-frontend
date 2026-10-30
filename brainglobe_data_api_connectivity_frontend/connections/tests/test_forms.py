import pytest

from brainglobe_data_api_connectivity_frontend.connections.forms import BestPathForm
from brainglobe_data_api_connectivity_frontend.connections.forms import (
    DirectConnectionsBetweenForm,
)
from brainglobe_data_api_connectivity_frontend.connections.forms import (
    DirectConnectionsForm,
)


@pytest.fixture
def expected_node_as_choices():
    return {"ANY": "any", "OUTPUT": "target", "INPUT": "source"}


@pytest.fixture
def expected_lookup_choices():
    return {"ALL": "all", "REPORTED": "reported"}


@pytest.mark.parametrize(
    ("sex", "expected_region_choices"),
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
            {
                "hotel": "hotel",
                "india": "india",
                "juliett": "juliett",
                "kilo": "kilo",
            },
            id="male",
        ),
    ],
)
class TestQueryForms:
    """Test all query forms, including male / female region completion."""

    def test_direct_connections_form(
        self,
        sex,
        expected_region_choices,
        expected_node_as_choices,
        expected_lookup_choices,
    ):
        """Test choices are correctly populated from graph."""

        form = DirectConnectionsForm(sex=sex)
        region_choices = dict(form.fields["region"].choices)  # type: ignore[attr-defined]
        node_as_choices = dict(form.fields["node_as"].choices)  # type: ignore[attr-defined]
        connections_lookup_choices = dict(form.fields["connections_lookup"].choices)  # type: ignore[attr-defined]

        assert region_choices == expected_region_choices
        assert node_as_choices == expected_node_as_choices
        assert connections_lookup_choices == expected_lookup_choices

    def test_direct_connections_between_form(
        self,
        sex,
        expected_region_choices,
        expected_node_as_choices,
        expected_lookup_choices,
    ):
        """Test choices are correctly populated from graph."""

        form = DirectConnectionsBetweenForm(sex=sex)
        region0_choices = dict(form.fields["region0"].choices)  # type: ignore[attr-defined]
        region1_choices = dict(form.fields["region1"].choices)  # type: ignore[attr-defined]
        node0_as_choices = dict(form.fields["node0_as"].choices)  # type: ignore[attr-defined]
        connections_lookup_choices = dict(form.fields["connections_lookup"].choices)  # type: ignore[attr-defined]

        assert region0_choices == expected_region_choices
        assert region1_choices == expected_region_choices
        assert node0_as_choices == expected_node_as_choices
        assert connections_lookup_choices == expected_lookup_choices

    def test_best_path_form(self, sex, expected_region_choices):
        """Test choices are correctly populated from graph."""

        form = BestPathForm(sex=sex)
        source_region_choices = dict(form.fields["region0"].choices)  # type: ignore[attr-defined]
        target_region_choices = dict(form.fields["region1"].choices)  # type: ignore[attr-defined]
        strategy_choices = dict(form.fields["strategy"].choices)  # type: ignore[attr-defined]

        assert source_region_choices == expected_region_choices
        assert target_region_choices == expected_region_choices
        assert strategy_choices == {
            "FEWEST_STEPS": "Fewest Steps",
            "WEAKEST_TOTAL_WEIGHT": "Weakest Total Weight",
            "WIDEST_PATH": "Widest Path",
        }
