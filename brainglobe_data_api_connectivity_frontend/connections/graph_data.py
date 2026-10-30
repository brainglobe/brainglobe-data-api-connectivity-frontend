import logging
from enum import StrEnum
from functools import cache
from typing import TYPE_CHECKING

import polars as pl
from brainglobe_data_api_connectivity.dijkstra import dijkstra
from brainglobe_data_api_connectivity.dijkstra.strategy import DijkstraStrategy
from brainglobe_data_api_connectivity.dijkstra.strategy import FewestSteps
from brainglobe_data_api_connectivity.dijkstra.strategy import WeakestTotalWeight
from brainglobe_data_api_connectivity.dijkstra.strategy import WidestPath
from brainglobe_data_api_connectivity.io.loaders import load_data

if TYPE_CHECKING:
    from brainglobe_data_api_connectivity.connections import Connections

logger = logging.getLogger(__name__)


class Sex(StrEnum):
    MALE = "male"
    FEMALE = "female"


class DijkstraStrategies(StrEnum):
    FEWEST_STEPS = "Fewest Steps"
    WEAKEST_TOTAL_WEIGHT = "Weakest Total Weight"
    WIDEST_PATH = "Widest Path"

    def get_instance(self) -> DijkstraStrategy:
        match self.name:
            case "FEWEST_STEPS":
                return FewestSteps()
            case "WEAKEST_TOTAL_WEIGHT":
                return WeakestTotalWeight()
            case "WIDEST_PATH":
                return WidestPath()
            case _:
                msg = f"Unknown strategy {self.name}"
                raise ValueError(msg)


@cache
def get_connections(sex: Sex) -> Connections:
    """
    Fetch a connections object for the specified sex.

    On first call (per sex), this loads the connections object from CSV files.
    Later calls return the cached, in-memory result instead.
    """
    logger.info("Loading connections object from file...")
    return load_data(sex)


def best_path(
    sex: Sex, source_region_id: str, target_region_id: str, strategy: DijkstraStrategies
) -> pl.DataFrame:
    """Find the optimal path between a source and target region.

    Parameters
    ----------
    sex : Sex
        The sex to query (male / female)
    source_region_id : str
        The source region id e.g. GPl_1
    target_region_id : str
        The target region id e.g. GPl_2
    strategy : DijkstraStrategies
        The strategy to use for finding the path

    Returns
    -------
    pl.DataFrame
        A polars dataframe with one column: region_id. Each row is one node,
        and they are in order of the best path.
    """

    connections = get_connections(sex)
    dijkstra_strategy = strategy.get_instance()

    node_indexes = []
    for region_id in [source_region_id, target_region_id]:
        node_index = connections.node_indexes_from_information(
            pl.col("region_id") == region_id
        )
        if len(node_index) != 1:
            msg = f"Found {len(node_index)} nodes with name {region_id}"
            raise ValueError(msg)

        node_indexes.append(node_index[0])

    path, _ = dijkstra(
        connections.network,
        source=node_indexes[0],
        target=node_indexes[1],
        strategy=dijkstra_strategy,
    )

    if path is None:
        return pl.DataFrame({"region_id": []})

    node_df = connections.node_information_from_index(path)
    node_index_col = "__node_index"

    # Force rows to be in order of given path via a left join.
    # This also ensures that any nodes missing node info still get a row
    # in the result df.
    result_df = pl.DataFrame(
        {node_index_col: path}, schema={node_index_col: node_df.schema[node_index_col]}
    )
    return result_df.join(node_df, on=node_index_col, how="left").select("region_id")
