from django.db import models


class QueryResult(models.Model):
    """Represents the result of a query against the connection graph."""

    result_file = models.FileField(upload_to="results")

    def __str__(self):
        return f"result_{self.id}"
