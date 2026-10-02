from django.db import models


class QueryResult(models.Model):
    """Represents the result of a query against the connection graph."""

    result_file = models.FileField(upload_to="results")
    n_rows = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"result_{self.id}"
