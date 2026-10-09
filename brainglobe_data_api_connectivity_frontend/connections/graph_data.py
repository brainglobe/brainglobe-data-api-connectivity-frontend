from enum import StrEnum
from typing import TYPE_CHECKING

import polars as pl
from brainglobe_data_api_connectivity.connections import Connections
from django.conf import settings

if TYPE_CHECKING:
    from brainglobe_data_api_connectivity.connections.query_opts import (
        ConnectionsLookup,
    )
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


def direct_connections(
    sex: Sex,
    node0: str,
    connections_lookup: ConnectionsLookup,
    node0_as: NodeIs,
    node1: str | None = None,
) -> pl.DataFrame:
    """Retrieve the direct connections of a node.

    Parameters
    ----------
    sex : Sex
        The sex to query (male / female)
    node0 : str
        The region id of node 0 e.g. GPl_1
    connections_lookup: ConnectionsLookup
        The source to use when searching for connections.
    node0_as : NodeIs
        The role of node_0 - INPUT, OUTPUT or ANY.
    node1: str, optional
        The region id of node 1 e.g. GPl_2

    Returns
    -------
    pl.DataFrame
        A polars dataframe with two columns: region_id and node_as
    """

    connections = get_connections(sex)

    # Look for direct connections of node0 (to any other node)
    if node1 is None:
        # Get index of node with specified region_id
        node_index = connections.node_indexes_from_information(
            pl.col("region_id") == node0
        )
        if len(node_index) != 1:
            msg = f"Found {len(node_index)} nodes with name {node0}"
            raise ValueError(msg)

        directs = connections.direct_connections(
            node_internal_index=node_index[0],
            node_as=node0_as,
            connections_lookup=connections_lookup,
        )

        result_dfs = []
        col_names = ["termination_region_id", "origin_region_id"]
        for node_list, col_name in zip(directs, col_names, strict=True):
            node_df = (
                connections.node_information_from_index(node_list)
                .select("region_id")
                .rename({"region_id": col_name})
            )
            result_dfs.append(node_df)

        result_df = pl.concat(result_dfs, how="diagonal").fill_null(node0)

        # make sure columns are in order (for ease of reading result)
        return result_df.select(["origin_region_id", "termination_region_id"])

    # Look for direct connections of node0 to node1
    directs = connections.direct_connection_between(
        node0={"region_id": node0},
        node1={"region_id": node1},
        connections_lookup=connections_lookup,
        node0_as=node0_as,
    )
    return directs.select(["origin_region_id", "termination_region_id"])
