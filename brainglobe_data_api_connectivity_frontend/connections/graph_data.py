from pathlib import Path

import polars as pl
from brainglobe_data_api_connectivity.connections import Connections


def get_connections() -> Connections:
    data_dir = Path(__file__).parent / "data"

    return Connections.from_files(
        node_info=data_dir / "small-nodes.csv",
        edge_table=data_dir / "small-edge-table.csv",
        edge_info=data_dir / "small-edge-meta.csv",
    )


def direct_connections(region_name: str) -> pl.DataFrame:

    # Get index of node with 'name=region_name'
    connections = get_connections()
    node_index = connections.node_indexes_from_information(
        pl.col("name") == region_name
    )
    if len(node_index) != 1:
        msg = f"Found {len(node_index)} nodes with name {region_name}"
        raise ValueError(msg)

    # Get names of nodes with direct connection
    directs = connections.direct_connections(node_internal_index=node_index[0])

    result_dfs = []
    for node_list, node_as in zip(directs, ["input", "output"], strict=True):
        node_df = connections.node_information_from_index(node_list).select("name")
        node_df = node_df.with_columns(pl.lit(node_as).alias("node_as"))
        result_dfs.append(node_df)

    return pl.concat(result_dfs)
