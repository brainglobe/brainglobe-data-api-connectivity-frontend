import polars as pl
import pytest
from brainglobe_data_api_connectivity.connections import Connections
from polars.testing import assert_frame_equal

from brainglobe_data_api_connectivity_frontend.connections.graph_data import (
    DijkstraStrategies,
)
from brainglobe_data_api_connectivity_frontend.connections.graph_data import Sex
from brainglobe_data_api_connectivity_frontend.connections.graph_data import best_path


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
