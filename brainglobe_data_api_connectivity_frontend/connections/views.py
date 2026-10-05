from typing import TYPE_CHECKING

from brainglobe_data_api_connectivity.connections.query_opts import NodeIs
from django.core.files.base import ContentFile
from django.http import FileResponse
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from brainglobe_data_api_connectivity_frontend.connections.graph_data import Sex
from brainglobe_data_api_connectivity_frontend.connections.graph_data import (
    direct_connections,
)

from .forms import DirectConnectionsForm
from .models import QueryResult

if TYPE_CHECKING:
    from django.http import HttpRequest


def browse_connections(request: HttpRequest, sex: str) -> HttpResponse:

    if sex not in Sex:
        msg = f"Provided sex must be one of {list(Sex)}"
        raise Http404(msg)

    if request.method == "POST":
        form = DirectConnectionsForm(request.POST, sex=sex)

        if form.is_valid():
            node_as = NodeIs[form.cleaned_data["node_as"]]
            result_df = direct_connections(
                sex=sex, region_id=form.cleaned_data["region"], node_as=node_as
            )

            query_result = QueryResult(sex=sex, n_rows=len(result_df))
            query_result.result_file.save(
                name="results.csv", content=ContentFile(result_df.write_csv())
            )
            query_result.save()

            return redirect("connections:results", result_id=query_result.id)
    else:
        form = DirectConnectionsForm(sex=sex)

    return render(
        request, "connections/browse_connections.html", {"form": form, "sex": sex}
    )


def results(request: HttpRequest, result_id: int) -> HttpResponse:

    result = get_object_or_404(QueryResult, id=result_id)
    return render(request, "connections/results.html", {"result": result})


def download_results(request: HttpRequest, result_id: int) -> HttpResponse:

    result = get_object_or_404(QueryResult, id=result_id)
    if not result.result_file:
        msg = "File no longer available"
        raise Http404(msg)

    return FileResponse(
        result.result_file.open("rb"),
        as_attachment=True,
    )
