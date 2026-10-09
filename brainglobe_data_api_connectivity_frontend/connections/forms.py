from brainglobe_data_api_connectivity.connections.query_opts import ConnectionsLookup
from brainglobe_data_api_connectivity.connections.query_opts import NodeIs
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from . import graph_data


def _fetch_region_ids(sex: str):
    """Fetch available region ids to populate dropdown menu"""

    connections = graph_data.get_connections(sex)

    names = sorted(connections.nodes["region_id"])
    return [(name, name) for name in names]


class DirectConnectionsForm(forms.Form):
    """Form to query direct connections of a node"""

    node0 = forms.ChoiceField(
        label="Node 0",
        required=True,
    )

    node1 = forms.ChoiceField(
        label="Node 1",
        required=False,
    )

    connections_lookup = forms.ChoiceField(
        label="Connections lookup",
        choices=[(option.name, option.name) for option in ConnectionsLookup],
        required=True,
    )

    node_as = forms.ChoiceField(
        label="Node 0 as",
        choices=[(option.name, option.name) for option in NodeIs],
        required=True,
    )

    def __init__(self, *args, sex: str, **kwargs):
        super().__init__(*args, **kwargs)

        region_ids = _fetch_region_ids(sex)
        # Add blank option for optional node_1
        region_ids_with_blank = [("", "------"), *region_ids]

        self.fields["node0"].choices = region_ids
        self.fields["node1"].choices = region_ids_with_blank

        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))
