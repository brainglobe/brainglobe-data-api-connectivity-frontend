from django.db import models


class QueryResult(models.Model):
    """Represents the result of a query against the connection graph."""

    created_at = models.DateTimeField(auto_now_add=True)
    sex = models.CharField(max_length=6)
    result_file = models.FileField(upload_to="results")
    n_rows = models.PositiveIntegerField()

    def __str__(self):
        return f"result_{self.id}"
