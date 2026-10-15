from brainglobe_data_api_connectivity.connections.query_opts import NodeIs
from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.helper import Layout
from crispy_forms.helper import reverse
from django import forms

from . import graph_data


def _fetch_regions(sex: str) -> list[tuple[str, str]]:
    """Fetch available region names / indexes to populate dropdown menu"""

    connections = graph_data.get_connections(sex)

    names = sorted(connections.nodes["region_id"])
    return [(name, name) for name in names]


class BaseQueryForm(forms.Form):
    def __init__(self, *args, sex: str, **kwargs) -> None:
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

    node_as = forms.ChoiceField(
        label="Node as",
        choices=[(option.name, option.name) for option in NodeIs],
        required=True,
    )

    def __init__(self, *args, sex: str, **kwargs) -> None:
        super().__init__(*args, sex=sex, **kwargs)
        self.fields["region"].choices = _fetch_regions(sex)
        self.helper.form_action = reverse(
            "connections:run_direct_query", args=[self.sex]
        )


class ShortestPathForm(BaseQueryForm):
    """Form to query the path between two nodes."""

    region0 = forms.ChoiceField(
        label="Input region name",
        required=True,
    )

    region1 = forms.ChoiceField(
        label="Output region name",
        required=True,
    )

    node_as = forms.ChoiceField(
        label="Node as",
        choices=[(option.name, option.name) for option in NodeIs],
        required=True,
    )

    def __init__(self, *args, sex: str, **kwargs) -> None:
        super().__init__(*args, sex=sex, **kwargs)

        regions = _fetch_regions(sex)
        self.fields["region0"].choices = regions
        self.fields["region1"].choices = regions
        self.helper.form_action = reverse("connections:run_path_query", args=[self.sex])
