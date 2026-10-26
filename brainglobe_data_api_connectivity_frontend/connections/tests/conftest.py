import pytest

from .helpers import load_test_data


@pytest.fixture(autouse=True, scope="session")
def mock_load_data(session_mocker) -> None:
    """Force load_data to return the test_data for all tests."""

    session_mocker.patch(
        "brainglobe_data_api_connectivity_frontend.connections.graph_data.load_data",
        side_effect=load_test_data,
    )
