from typing import TYPE_CHECKING

from django.core.files.base import ContentFile
from django.http import FileResponse
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.http import require_POST

from brainglobe_data_api_connectivity_frontend.connections.graph_data import Sex

from .forms import QUERY_FORMS
from .forms import DirectConnectionsForm
from .forms import ShortestPathForm
from .models import QueryResult

if TYPE_CHECKING:
    from django.http import HttpRequest


def _check_sex_valid(sex: str) -> None:
    if sex not in Sex:
        msg = f"Provided sex must be one of {[sex.value for sex in Sex]}"
        raise Http404(msg)


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
def run_query(request: HttpRequest, sex: str, query_type: str) -> HttpResponse:

    # Find the correct form class based on 'query_type'
    form_class = QUERY_FORMS.get(query_type)
    if form_class is None:
        msg = f"Unknown query type {query_type}"
        raise Http404(msg)

    # Show browse page if form is invalid
    form = form_class(request.POST, sex=sex)
    if not form.is_valid():
        redirect("connections:browse_connections", sex=sex)

    # Run query and handle result
    result_df = form.run_query()
    query_result = QueryResult(sex=sex, n_rows=len(result_df))
    query_result.result_file.save(
        name="results.csv", content=ContentFile(result_df.write_csv())
    )
    query_result.save()

    return redirect("connections:results", result_id=query_result.id)


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
