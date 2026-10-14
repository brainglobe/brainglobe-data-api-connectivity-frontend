import polars as pl
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
    query_type = None

    def run_query(self) -> pl.DataFrame:
        raise NotImplementedError

    def _check_form_ready(self) -> None:
        if not self.is_bound or not self.is_valid():
            msg = "form must be bound and valid"
            raise ValueError(msg)

    def __init__(self, *args, sex: str, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.sex = sex
        self.helper = FormHelper()
        self.helper.form_class = "query-form"
        self.helper.form_action = reverse(
            "connections:run_query", args=[self.sex, self.query_type]
        )
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

    query_type = "direct"

    region = forms.ChoiceField(
        label="Region name",
        required=True,
    )

    node_as = forms.ChoiceField(
        label="Node as",
        choices=[(option.name, option.name) for option in NodeIs],
        required=True,
    )

    def run_query(self) -> pl.DataFrame:
        self._check_form_ready()

        node_as = NodeIs[self.cleaned_data["node_as"]]
        return graph_data.direct_connections(
            sex=self.sex, region_id=self.cleaned_data["region"], node_as=node_as
        )

    def __init__(self, *args, sex: str, **kwargs) -> None:
        super().__init__(*args, sex=sex, **kwargs)
        self.fields["region"].choices = _fetch_regions(sex)


class ShortestPathForm(BaseQueryForm):
    """Form to query the path between two nodes."""

    query_type = "path"

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

    def run_query(self) -> pl.DataFrame:
        self._check_form_ready()
        return pl.DataFrame()

    def __init__(self, *args, sex: str, **kwargs) -> None:
        super().__init__(*args, sex=sex, **kwargs)

        regions = _fetch_regions(sex)
        self.fields["region0"].choices = regions
        self.fields["region1"].choices = regions


QUERY_FORMS = {
    form.query_type: form for form in [DirectConnectionsForm, ShortestPathForm]
}
