from enum import StrEnum
from typing import TYPE_CHECKING

import polars as pl
from brainglobe_data_api_connectivity.connections import Connections
from django.conf import settings

if TYPE_CHECKING:
    from brainglobe_data_api_connectivity.connections.query_opts import NodeIs


class Sex(StrEnum):
    MALE = "male"
    FEMALE = "female"


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
