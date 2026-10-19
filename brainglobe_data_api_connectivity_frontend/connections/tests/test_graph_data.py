import polars as pl
import pytest
from polars.testing import assert_frame_equal

from brainglobe_data_api_connectivity_frontend.connections.graph_data import (
    DijkstraStrategies,
)
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
        sex="female",
        source_region_id="charlie",
        target_region_id="echo",
        strategy=strategy,
    )
    assert_frame_equal(result_df, expected_result)
