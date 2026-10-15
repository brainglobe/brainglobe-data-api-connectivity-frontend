from typing import TYPE_CHECKING

import polars as pl
from brainglobe_data_api_connectivity.connections.query_opts import NodeIs
from django.core.files.base import ContentFile
from django.http import FileResponse
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.http import require_POST

from brainglobe_data_api_connectivity_frontend.connections.graph_data import Sex
from brainglobe_data_api_connectivity_frontend.connections.graph_data import (
    direct_connections,
)

from .forms import DirectConnectionsForm
from .forms import ShortestPathForm
from .models import QueryResult

if TYPE_CHECKING:
    from django.http import HttpRequest


def _check_sex_valid(sex: str) -> None:
    if sex not in Sex:
        msg = f"Provided sex must be one of {[sex.value for sex in Sex]}"
        raise Http404(msg)


def _handle_query_result(result_df: pl.DataFrame, sex: Sex) -> HttpResponse:
    query_result = QueryResult(sex=sex, n_rows=len(result_df))
    query_result.result_file.save(
        name="results.csv", content=ContentFile(result_df.write_csv())
    )
    query_result.save()

    return redirect("connections:results", result_id=query_result.id)


def browse_connections(request: HttpRequest, sex: str) -> HttpResponse:
    """Main page for browsing connections of a specific sex."""

    _check_sex_valid(sex)
    connections_form = DirectConnectionsForm(sex=sex)
    path_form = ShortestPathForm(sex=sex)

    return render(
        request,
        "connections/browse_connections.html",
        {"connections_form": connections_form, "path_form": path_form, "sex": sex},
    )


@require_POST
def run_direct_connections_query(request: HttpRequest, sex: str) -> HttpResponse:

    _check_sex_valid(sex)
    form = DirectConnectionsForm(request.POST, sex=sex)

    if form.is_valid():
        node_as = NodeIs[form.cleaned_data["node_as"]]
        result_df = direct_connections(
            sex=sex, region_id=form.cleaned_data["region"], node_as=node_as
        )
        return _handle_query_result(result_df, sex)

    return redirect("connections:browse_connections", sex=sex)


@require_POST
def run_path_query(request: HttpRequest, sex: str) -> HttpResponse:

    _check_sex_valid(sex)
    form = ShortestPathForm(request.POST, sex=sex)

    if form.is_valid():
        result_df = pl.DataFrame()
        return _handle_query_result(result_df, sex)

    return redirect("connections:browse_connections", sex=sex)


def results(request: HttpRequest, result_id: int) -> HttpResponse:
    """View summary of query results."""

    result = get_object_or_404(QueryResult, id=result_id)
    return render(request, "connections/results.html", {"result": result})


def download_results(request: HttpRequest, result_id: int) -> HttpResponse:
    """Download stored results file."""

    result = get_object_or_404(QueryResult, id=result_id)
    if not result.result_file:
        msg = "File no longer available"
        raise Http404(msg)

    return FileResponse(
        result.result_file.open("rb"),
        as_attachment=True,
    )
