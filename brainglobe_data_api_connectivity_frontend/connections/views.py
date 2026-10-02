from typing import TYPE_CHECKING

from django.core.files.base import ContentFile
from django.http import FileResponse
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from brainglobe_data_api_connectivity_frontend.connections.graph_data import (
    direct_connections,
)

from .forms import DirectConnectionsForm
from .models import QueryResult

if TYPE_CHECKING:
    from django.http import HttpRequest


def browse_connections(request: HttpRequest) -> HttpResponse:

    if request.method == "POST":
        form = DirectConnectionsForm(request.POST)
        if form.is_valid():
            result_df = direct_connections(form.cleaned_data["region"])
            query_result = QueryResult(success=True, n_rows=len(result_df))
            query_result.result_file.save(
                name="results.csv", content=ContentFile(result_df.write_csv())
            )
            query_result.save()
            return redirect("connections:results", result_id=query_result.id)
    else:
        form = DirectConnectionsForm()

    return render(request, "connections/browse_connections.html", {"form": form})


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
