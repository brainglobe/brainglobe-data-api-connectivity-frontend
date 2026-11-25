import csv
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from brainglobe_data_api_connectivity.connections.query_opts import ConnectionsLookup
from brainglobe_data_api_connectivity.connections.query_opts import NodeIs
from django.core.files.base import ContentFile
from django.http import FileResponse
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
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
from .forms import DirectConnectionsBetweenForm
from .forms import DirectConnectionsForm
from .forms import _fetch_regions
from .models import QueryResult

if TYPE_CHECKING:
    import polars as pl
    from django.http import HttpRequest

# Result columns containing region ids, to display as full region names
REGION_ID_COLUMNS = {
    "from",
    "to",
    "region_id",
    "origin_region_id",
    "termination_region_id",
}

# Pairs of (from, to) result columns, used to split results by direction
EDGE_COLUMNS = [("from", "to"), ("origin_region_id", "termination_region_id")]

# Evidence columns not shown on the evidence page, as they are internal or
# repeat the connection's regions
EVIDENCE_HIDDEN_COLUMNS = {
    "__idx_from",
    "__idx_to",
    "origin_region_idx",
    "termination_region_idx",
    "origin_region_id",
    "termination_region_id",
    "connection_origin_region_side",
    "connection_origin_region_abbr",
    "connection_termination_region_side",
    "connection_termination_region_abbr",
}


def _get_valid_sex(sex: str) -> Sex:
    """Check the provided sex is valid and return the matching enum."""

    try:
        return Sex(sex)
    except ValueError as e:
        msg = f"Provided sex must be one of {[sex.value for sex in Sex]}"
        raise Http404(msg) from e


def _handle_query_result(
    result_df: pl.DataFrame, sex: Sex, region_id: str = ""
) -> HttpResponse:
    """Save result_df to csv and create a record in the database"""

    query_result = QueryResult(sex=sex, n_rows=len(result_df), region_id=region_id)
    query_result.result_file.save(
        name="results.csv", content=ContentFile(result_df.write_csv())
    )
    query_result.save()

    return redirect("connections:results", result_id=query_result.id)


def browse_connections(request: HttpRequest, sex: str) -> HttpResponse:
    """Main page for browsing connections of a specific sex."""

    sex = _get_valid_sex(sex)
    connections_form = DirectConnectionsForm(sex=sex)
    connections_between_form = DirectConnectionsBetweenForm(sex=sex)
    path_form = BestPathForm(sex=sex)

    return render(
        request,
        "connections/browse_connections.html",
        {
            "connections_form": connections_form,
            "connections_between_form": connections_between_form,
            "path_form": path_form,
            "sex": sex,
        },
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
        return _handle_query_result(result_df, sex, form.cleaned_data["region"])

    return redirect("connections:browse_connections", sex=sex)


@require_POST
def run_direct_connections_between_query(
    request: HttpRequest, sex: str
) -> HttpResponse:
    """Run a direct connections between query, using the submitted form data."""

    sex = _get_valid_sex(sex)
    form = DirectConnectionsBetweenForm(request.POST, sex=sex)

    if form.is_valid():
        node0_as = NodeIs[form.cleaned_data["node0_as"]]
        connections_lookup = ConnectionsLookup[form.cleaned_data["connections_lookup"]]

        result_df = get_connections(sex).direct_connection_between(
            node0={"region_id": form.cleaned_data["region0"]},
            node1={"region_id": form.cleaned_data["region1"]},
            connections_lookup=connections_lookup,
            node0_as=node0_as,
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


def _split_by_direction(
    header: list[str], rows: list[list[str]], region_id: str
) -> list[tuple[str, list[str], list[list[str]]]]:
    """Split edge rows into projections from / to region_id.

    Returns a list of (direction, header, rows), dropping the column that
    always holds region_id. Returns an empty list if there are no edge columns.
    """

    for from_col, to_col in EDGE_COLUMNS:
        if from_col in header and to_col in header:
            break
    else:
        return []

    tables = []
    for direction, column in [("from", from_col), ("to", to_col)]:
        i = header.index(column)
        tables.append(
            (
                direction,
                header[:i] + header[i + 1 :],
                [row[:i] + row[i + 1 :] for row in rows if row[i] == region_id],
            )
        )
    return tables


def results(request: HttpRequest, result_id: int) -> HttpResponse:
    """View summary of query results."""

    result = get_object_or_404(QueryResult, id=result_id)

    header, rows = [], []
    if result.result_file:
        with result.result_file.open("r") as f:
            reader = csv.reader(f)
            header = next(reader, [])
            rows = list(reader)

    # Add a link to the evidence for each connection
    if "from" in header and "to" in header:
        i_from, i_to = header.index("from"), header.index("to")
        evidence_url = reverse("connections:connection_evidence", args=[result.sex])
        header.append("evidence")
        for row in rows:
            row.append(
                f"{evidence_url}?{urlencode({'from': row[i_from], 'to': row[i_to]})}"
            )

    region_names = dict(_fetch_regions(Sex(result.sex)))

    tables = [("", header, rows)] if header else []
    if result.region_id:
        region_name = region_names.get(result.region_id, result.region_id)
        tables = [
            (f"Projections {direction} {region_name}", table_header, table_rows)
            for direction, table_header, table_rows in _split_by_direction(
                header, rows, result.region_id
            )
            if table_rows
        ] or tables

    for _, table_header, table_rows in tables:
        for i, column in enumerate(table_header):
            if column in REGION_ID_COLUMNS:
                for row in table_rows:
                    row[i] = region_names.get(row[i], row[i])
            elif column == "value":
                table_header[i] = "strength"

    return render(
        request,
        "connections/results.html",
        {"result": result, "tables": tables},
    )


def connection_evidence(request: HttpRequest, sex: str) -> HttpResponse:
    """View all evidence (reports, papers etc.) for one connection."""

    sex = _get_valid_sex(sex)
    region_names = dict(_fetch_regions(sex))
    from_id, to_id = request.GET.get("from"), request.GET.get("to")
    if from_id not in region_names or to_id not in region_names:
        msg = "Unknown region"
        raise Http404(msg)

    evidence_df = get_connections(sex).direct_connection_between(
        node0={"region_id": from_id},
        node1={"region_id": to_id},
        connections_lookup=ConnectionsLookup.ALL,
        node0_as=NodeIs.INPUT,
    )
    evidence_df = evidence_df.drop(EVIDENCE_HIDDEN_COLUMNS, strict=False)

    return render(
        request,
        "connections/evidence.html",
        {
            "title": f"{region_names[from_id]} to {region_names[to_id]}",
            "header": evidence_df.columns,
            "rows": evidence_df.rows(),
        },
    )


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
