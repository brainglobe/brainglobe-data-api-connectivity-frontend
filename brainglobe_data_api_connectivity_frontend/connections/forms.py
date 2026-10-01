from django import forms

from . import graph_data


def _fetch_regions():
    """Fetch available region names / indexes to populate dropdown menu"""

    connections = graph_data.get_connections()

    names = connections.nodes["name"]
    return [(name, name) for name in names]


class DirectConnectionsForm(forms.Form):
    """Form to query direct connections of a node"""

    regions = forms.ChoiceField(
        label="Region name",
        choices=_fetch_regions,
        required=True,
    )
