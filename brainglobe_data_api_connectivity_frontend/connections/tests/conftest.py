from typing import TYPE_CHECKING

import pytest

from .helpers import load_test_data

if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def mock_load_data(mocker) -> MagicMock:
    """
    Force load_data to return the local test data (rather than downloading
    the real dataset).
    """

    return mocker.patch(
        "brainglobe_data_api_connectivity_frontend.connections.graph_data.load_data",
        side_effect=load_test_data,
    )
