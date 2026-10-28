from datetime import timedelta
from pathlib import Path

from brainglobe_data_api_connectivity.connections import Connections
from django.core.files.base import ContentFile
from django.utils import timezone

from brainglobe_data_api_connectivity_frontend.connections.graph_data import Sex
from brainglobe_data_api_connectivity_frontend.connections.models import QueryResult


def load_test_data(sex: Sex) -> Connections:
    """Load the test data Connections object."""

    identifier = "CNS2m" if sex == Sex.MALE else "CNS2f"

    sex_dir = Path(__file__).parent / "data" / identifier
    return Connections.from_files(
        node_info=sex_dir / f"{identifier}_node_info.csv",
        edge_table=sex_dir / f"{identifier}_edge_table.csv",
        edge_info=sex_dir / f"{identifier}_edge_info.csv",
        edge_info_from_col="origin_region_idx",
        edge_info_to_col="termination_region_idx",
        node_index_column="region_idx",
    )


def create_query_result(
    *,
    minutes_ago: int = 0,
    result_file: bool = True,
) -> QueryResult:
    """Create a new QueryResult in the database.

    Parameters
    ----------
    minutes_ago : int, optional
        Overwrite the default created_at value (normally the
        current time) with current time - minutes_ago.
    result_file : bool, optional
        Whether to include a results file.

    Returns
    -------
    QueryResult
        The created QueryResult
    """

    result = QueryResult(sex="female", n_rows=876)
    if result_file:
        result.result_file.save(name="test", content=ContentFile("hello world"))

    result.save()  # Automatically sets created_at as the current time

    if minutes_ago != 0:
        # Overwrite the default created_at time
        result.created_at = timezone.now() - timedelta(minutes=minutes_ago)
        result.save()

    return result
