from brainglobe_data_api_connectivity.connections.query_opts import ConnectionsLookup
from brainglobe_data_api_connectivity.connections.query_opts import NodeIs
from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.helper import Layout
from crispy_forms.helper import reverse
from django import forms

from .graph_data import DijkstraStrategies
from .graph_data import Sex
from .graph_data import get_connections


def _fetch_regions(sex: Sex) -> list[tuple[str, str]]:
    """Fetch available region names / indexes to populate dropdown menu"""

    connections = get_connections(sex)

    names = sorted(connections.nodes["region_id"])
    return [(name, name) for name in names]


def _create_node_as_field(label: str = "Node as") -> forms.ChoiceField:
    """Create a field for the NodeIs enum."""

    return forms.ChoiceField(
        label=label,
        choices=[(option.name, option.value) for option in NodeIs],
        required=True,
        initial=NodeIs.ANY.name,
    )


def _create_connections_lookup_field(
    label: str = "Connections lookup",
) -> forms.ChoiceField:
    """Create a field for teh ConnectionsLookup enum."""

    return forms.ChoiceField(
        label=label,
        choices=[(option.name, option.value) for option in ConnectionsLookup],
        required=True,
        initial=ConnectionsLookup.REPORTED.name,
    )


class BaseQueryForm(forms.Form):
    """Base query form to establish shared layout / settings for all forms."""

    def __init__(self, *args, sex: Sex, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.sex = sex
        self.helper = FormHelper()
        self.helper.form_class = "query-form"
        self.helper.layout = Layout(
            *self.fields,
            StrictButton(
                '<span class="query-spinner spinner-border spinner-border-sm '
                'd-none" aria-hidden="true"></span> '
                '<span role="status" class="query-text">Submit</span>',
                type="submit",
                css_class="btn btn-primary submit-query-btn",
            ),
        )


class DirectConnectionsForm(BaseQueryForm):
    """Form to query direct connections of a node"""

    region = forms.ChoiceField(
        label="Region name",
        required=True,
    )

    node_as = _create_node_as_field()

    connections_lookup = _create_connections_lookup_field()

    return_edges = forms.BooleanField(
        label="Return edges", required=False, initial=False
    )

    def __init__(self, *args, sex: Sex, **kwargs) -> None:
        super().__init__(*args, sex=sex, **kwargs)
        self.fields["region"].choices = _fetch_regions(sex)  # type: ignore[attr-defined]
        self.helper.form_action = reverse(
            "connections:run_direct_query", args=[self.sex]
        )


class DirectConnectionsBetweenForm(BaseQueryForm):
    """Form to query direct connections between two nodes"""

    region0 = forms.ChoiceField(
        label="First region name",
        required=True,
    )

    region1 = forms.ChoiceField(
        label="Second region name",
        required=True,
    )

    node0_as = _create_node_as_field(label="First region as")

    connections_lookup = _create_connections_lookup_field()

    def __init__(self, *args, sex: Sex, **kwargs) -> None:
        super().__init__(*args, sex=sex, **kwargs)
        regions = _fetch_regions(sex)
        self.fields["region0"].choices = regions  # type: ignore[attr-defined]
        self.fields["region1"].choices = regions  # type: ignore[attr-defined]
        self.helper.form_action = reverse(
            "connections:run_direct_between_query", args=[self.sex]
        )


class BestPathForm(BaseQueryForm):
    """Form to query the path between two nodes."""

    region0 = forms.ChoiceField(
        label="Source region name",
        required=True,
    )

    region1 = forms.ChoiceField(
        label="Target region name",
        required=True,
    )

    strategy = forms.ChoiceField(
        label="Strategy",
        choices=[(option.name, option.value) for option in DijkstraStrategies],
        required=True,
    )

    def __init__(self, *args, sex: Sex, **kwargs) -> None:
        super().__init__(*args, sex=sex, **kwargs)

        regions = _fetch_regions(sex)
        self.fields["region0"].choices = regions  # type: ignore[attr-defined]
        self.fields["region1"].choices = regions  # type: ignore[attr-defined]
        self.helper.form_action = reverse("connections:run_path_query", args=[self.sex])
