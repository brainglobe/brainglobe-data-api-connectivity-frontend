from brainglobe_data_api_connectivity.connections.query_opts import NodeIs
from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.helper import Layout
from django import forms

from . import graph_data


def _fetch_regions(sex: str):
    """Fetch available region names / indexes to populate dropdown menu"""

    connections = graph_data.get_connections(sex)

    names = sorted(connections.nodes["region_id"])
    return [(name, name) for name in names]


class DirectConnectionsForm(forms.Form):
    """Form to query direct connections of a node"""

    region = forms.ChoiceField(
        label="Region name",
        required=True,
    )

    node_as = forms.ChoiceField(
        label="Node as",
        choices=[(option.name, option.name) for option in NodeIs],
        required=True,
    )

    def __init__(self, *args, sex: str, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["region"].choices = _fetch_regions(sex)
        self.helper = FormHelper()
        self.helper.form_class = "query-form"
        self.helper.layout = Layout(
            "region",
            "node_as",
            StrictButton(
                '<span class="query-spinner spinner-border spinner-border-sm '
                'd-none" aria-hidden="true"></span> '
                '<span role="status" class="query-text">Submit</span>',
                type="submit",
                css_class="btn btn-primary submit-query-btn",
            ),
        )
