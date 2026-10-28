import os
from pathlib import Path

import polars as pl
import pytest
from brainglobe_data_api_connectivity.connections import Connections
from brainglobe_data_api_connectivity.io.loaders import GIN_REPO
from polars.testing import assert_frame_equal

from brainglobe_data_api_connectivity_frontend.connections.graph_data import (
    DijkstraStrategies,
)
from brainglobe_data_api_connectivity_frontend.connections.graph_data import Sex
from brainglobe_data_api_connectivity_frontend.connections.graph_data import best_path
from brainglobe_data_api_connectivity_frontend.connections.graph_data import (
    get_connections,
)

from .helpers import load_test_data


def test_get_connections_cache(mock_load_data):
    """Test the result of get_connections is cached for male / female."""

    expected_female_data = load_test_data(Sex.FEMALE)
    expected_male_data = load_test_data(Sex.MALE)

    # Invalidate the get_connections in-memory cache
    get_connections.cache_clear()

    # Multiple calls to get_connections(MALE) should only call load_data once
    # (rest use cache)
    expected_total_calls = 1
    for _ in range(3):
        male_data = get_connections(Sex.MALE)
        assert_frame_equal(male_data.nodes, expected_male_data.nodes)
        assert mock_load_data.call_count == expected_total_calls

    # Multiple calls to get_connections(FEMALE) should only call load_data once
    # (rest use cache)
    expected_total_calls += 1
    for _ in range(3):
        female_data = get_connections(Sex.FEMALE)
        assert_frame_equal(female_data.nodes, expected_female_data.nodes)
        assert mock_load_data.call_count == expected_total_calls


def test_get_connections_pooch_dir():
    """Test that NEUROME_DATA_DIR is set, and is used as the pooch dir."""

    pooch_dir = Path(os.environ["NEUROME_DATA_DIR"])
    assert GIN_REPO.abspath == pooch_dir


@pytest.mark.parametrize(
    ("strategy", "expected_result"),
    [
        pytest.param(
            DijkstraStrategies.FEWEST_STEPS,
            pl.DataFrame(
                data={
                    "region_id": ["charlie", "alpha", "echo"],
                }
            ),
            id="Fewest steps",
        ),
        pytest.param(
            DijkstraStrategies.WEAKEST_TOTAL_WEIGHT,
            pl.DataFrame(
                data={
                    "region_id": ["charlie", "bravo", "alpha", "echo"],
                }
            ),
            id="Weakest total weight",
        ),
        pytest.param(
            DijkstraStrategies.WIDEST_PATH,
            pl.DataFrame(
                data={
                    "region_id": ["charlie", "delta", "echo"],
                }
            ),
            id="Widest path",
        ),
    ],
)
def test_best_path_strategies(strategy, expected_result):
    """
    Check that using different Dijkstra strategies returns the correct result.
    """

    result_df = best_path(
        sex=Sex.FEMALE,
        source_region_id="charlie",
        target_region_id="echo",
        strategy=strategy,
    )
    assert_frame_equal(result_df, expected_result)


@pytest.mark.parametrize(
    ("source_region_id", "target_region_id"),
    [
        pytest.param(
            "INVALID",
            "charlie",
            id="Source invalid",
        ),
        pytest.param(
            "charlie",
            "INVALID",
            id="Target invalid",
        ),
        pytest.param(
            "INVALID",
            "INVALID-2",
            id="Both invalid",
        ),
    ],
)
def test_best_path_with_invalid_region(source_region_id, target_region_id):
    """Test that querying an invalid region id raises a ValueError"""

    with pytest.raises(ValueError, match=r"Found 0 nodes with name INVALID"):
        best_path(
            sex=Sex.FEMALE,
            source_region_id=source_region_id,
            target_region_id=target_region_id,
            strategy=DijkstraStrategies.FEWEST_STEPS,
        )


def test_no_available_path(mocker):
    """Test than an empty dataframe is returned when no path is found."""

    # The test data has no isolated nodes, so here we mock a graph with two
    # un-connected nodes
    mocker.patch(
        "brainglobe_data_api_connectivity_frontend.connections.graph_data.get_connections",
        return_value=Connections(
            node_info=pl.DataFrame({"region_id": ["a", "b"]}), edge_table=pl.DataFrame()
        ),
    )

    result_df = best_path(
        sex=Sex.FEMALE,
        source_region_id="a",
        target_region_id="b",
        strategy=DijkstraStrategies.FEWEST_STEPS,
    )
    assert_frame_equal(result_df, pl.DataFrame({"region_id": []}))
