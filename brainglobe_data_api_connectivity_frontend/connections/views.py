from typing import TYPE_CHECKING

from django.shortcuts import render

from .forms import DirectConnectionsForm

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.http import HttpResponse


def browse_connections(request: HttpRequest) -> HttpResponse:

    if request.method == "POST":
        form = DirectConnectionsForm(request.POST)
        if form.is_valid():
            pass

    else:
        form = DirectConnectionsForm()

    return render(request, "connections/browse_connections.html", {"form": form})
