from typing import TYPE_CHECKING

from brainglobe_data_api_connectivity.connections.query_opts import ConnectionsLookup
from brainglobe_data_api_connectivity.connections.query_opts import NodeIs
from django.core.files.base import ContentFile
from django.http import FileResponse
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.http import require_POST

from brainglobe_data_api_connectivity_frontend.connections.graph_data import (
    DijkstraStrategies,
)
from brainglobe_data_api_connectivity_frontend.connections.graph_data import Sex
from brainglobe_data_api_connectivity_frontend.connections.graph_data import best_path
from brainglobe_data_api_connectivity_frontend.connections.graph_data import (
    get_connections,
)

from .forms import BestPathForm
from .forms import DirectConnectionsForm
from .models import QueryResult

if TYPE_CHECKING:
    import polars as pl
    from django.http import HttpRequest


def _get_valid_sex(sex: str) -> Sex:
    """Check the provided sex is valid and return the matching enum."""

    try:
        return Sex(sex)
    except ValueError as e:
        msg = f"Provided sex must be one of {[sex.value for sex in Sex]}"
        raise Http404(msg) from e


def _handle_query_result(result_df: pl.DataFrame, sex: Sex) -> HttpResponse:
    """Save result_df to csv and create a record in the database"""

    query_result = QueryResult(sex=sex, n_rows=len(result_df))
    query_result.result_file.save(
        name="results.csv", content=ContentFile(result_df.write_csv())
    )
    query_result.save()

    return redirect("connections:results", result_id=query_result.id)


def browse_connections(request: HttpRequest, sex: str) -> HttpResponse:
    """Main page for browsing connections of a specific sex."""

    sex = _get_valid_sex(sex)
    connections_form = DirectConnectionsForm(sex=sex)
    path_form = BestPathForm(sex=sex)

    return render(
        request,
        "connections/browse_connections.html",
        {"connections_form": connections_form, "path_form": path_form, "sex": sex},
    )


@require_POST
def run_direct_connections_query(request: HttpRequest, sex: str) -> HttpResponse:
    """Run a direct connections query, using the submitted form data."""

    sex = _get_valid_sex(sex)
    form = DirectConnectionsForm(request.POST, sex=sex)

    if form.is_valid():
        node_as = NodeIs[form.cleaned_data["node_as"]]
        connections_lookup = ConnectionsLookup[form.cleaned_data["connections_lookup"]]

        result_df = get_connections(sex).direct_connection_info(
            node={"region_id": form.cleaned_data["region"]},
            node_as=node_as,
            connections_lookup=connections_lookup,
            return_edges=form.cleaned_data["return_edges"],
        )
        return _handle_query_result(result_df, sex)

    return redirect("connections:browse_connections", sex=sex)


@require_POST
def run_path_query(request: HttpRequest, sex: str) -> HttpResponse:
    """Run a path query, using the submitted form data."""

    sex = _get_valid_sex(sex)
    form = BestPathForm(request.POST, sex=sex)

    if form.is_valid():
        strategy = DijkstraStrategies[form.cleaned_data["strategy"]]
        result_df = best_path(
            sex=sex,
            source_region_id=form.cleaned_data["region0"],
            target_region_id=form.cleaned_data["region1"],
            strategy=strategy,
        )
        return _handle_query_result(result_df, sex)

    return redirect("connections:browse_connections", sex=sex)


def results(request: HttpRequest, result_id: int) -> HttpResponse:
    """View summary of query results."""

    result = get_object_or_404(QueryResult, id=result_id)
    return render(request, "connections/results.html", {"result": result})


def download_results(request: HttpRequest, result_id: int) -> FileResponse:
    """Download stored results file."""

    result = get_object_or_404(QueryResult, id=result_id)
    if not result.result_file:
        msg = "File no longer available"
        raise Http404(msg)

    return FileResponse(
        result.result_file.open("rb"),
        as_attachment=True,
    )
