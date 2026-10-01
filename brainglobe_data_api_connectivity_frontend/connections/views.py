import csv
from typing import TYPE_CHECKING

from django.core.files.base import ContentFile
from django.http import HttpResponse
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
            query_result = QueryResult()
            query_result.result_file.save(
                name="results.csv", content=ContentFile(result_df.write_csv())
            )
            query_result.save()
            return redirect("connections:results", result_id=query_result.id)
    else:
        form = DirectConnectionsForm()

    return render(request, "connections/browse_connections.html", {"form": form})


def results(request: HttpRequest, result_id: int) -> HttpResponse:
    return render(request, "connections/results.html")


def download_results(request: HttpRequest) -> HttpResponse:

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="result.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(["First row", "Foo", "Bar", "Baz"])
    writer.writerow(["Second row", "A", "B", "C", '"Testing"', "Here's a quote"])

    return response
