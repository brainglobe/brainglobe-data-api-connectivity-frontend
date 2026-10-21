from enum import StrEnum
from typing import TYPE_CHECKING

import polars as pl
from brainglobe_data_api_connectivity.connections import Connections
from brainglobe_data_api_connectivity.dijkstra import dijkstra
from brainglobe_data_api_connectivity.dijkstra.strategy import DijkstraStrategy
from brainglobe_data_api_connectivity.dijkstra.strategy import FewestSteps
from brainglobe_data_api_connectivity.dijkstra.strategy import WeakestTotalWeight
from brainglobe_data_api_connectivity.dijkstra.strategy import WidestPath
from django.conf import settings

if TYPE_CHECKING:
    from brainglobe_data_api_connectivity.connections.query_opts import NodeIs


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


def get_connections(sex: Sex) -> Connections:
    """
    Create a connections object for the specified sex.

    This function uses csv files stored inside settings.CONNECTIONS_DATA_DIR.
    This directory should contain one folder for each sex
    (identifiers: "CNS2m" / "CNS2f"), each containing:
    IDENTIFIER_node_info.csv, IDENTIFIER_edge_table.csv, and
    IDENTIFIER_edge_info.csv,
    """

    identifier = "CNS2m" if sex == Sex.MALE else "CNS2f"

    sex_dir = settings.CONNECTIONS_DATA_DIR / identifier
    return Connections.from_files(
        node_info=sex_dir / f"{identifier}_node_info.csv",
        edge_table=sex_dir / f"{identifier}_edge_table.csv",
        edge_info=sex_dir / f"{identifier}_edge_info.csv",
        edge_info_from_col="origin_region_idx",
        edge_info_to_col="termination_region_idx",
        node_index_column="region_idx",
    )


def direct_connections(sex: Sex, region_id: str, node_as: NodeIs) -> pl.DataFrame:
    """Retrieve the direct connections of a region.

    Parameters
    ----------
    sex : Sex
        The sex to query (male / female)
    region_id : str
        The region id e.g. GPl_1
    node_as : NodeIs
        The role of the region node - INPUT, OUTPUT or ANY.

    Returns
    -------
    pl.DataFrame
        A polars dataframe with two columns: region_id and node_as
    """

    # Get index of node with specified region_id
    connections = get_connections(sex)
    node_index = connections.node_indexes_from_information(
        pl.col("region_id") == region_id
    )
    if len(node_index) != 1:
        msg = f"Found {len(node_index)} nodes with name {region_id}"
        raise ValueError(msg)

    # Get ids of nodes with direct connection
    directs = connections.direct_connections(
        node_internal_index=node_index[0], node_as=node_as
    )

    result_dfs = []
    for node_list, source in zip(directs, ["input", "output"], strict=True):
        node_df = connections.node_information_from_index(node_list).select("region_id")
        node_df = node_df.with_columns(pl.lit(source).alias("node_as"))
        result_dfs.append(node_df)

    return pl.concat(result_dfs)


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
