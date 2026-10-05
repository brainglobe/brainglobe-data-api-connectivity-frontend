from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING

import polars as pl
from brainglobe_data_api_connectivity.connections import Connections

if TYPE_CHECKING:
    from brainglobe_data_api_connectivity.connections.query_opts import NodeIs


class Sex(StrEnum):
    MALE = "male"
    FEMALE = "female"


def get_connections(sex: Sex) -> Connections:

    data_dir = Path(__file__).parent / "data"
    identifier = "CNS2m" if sex == Sex.MALE else "CNS2f"

    sex_dir = data_dir / identifier
    return Connections.from_files(
        node_info=sex_dir / f"{identifier}_node_info.csv",
        edge_table=sex_dir / f"{identifier}_edge_table.csv",
        edge_info=sex_dir / f"{identifier}_edge_info.csv",
        edge_info_from_col="origin_region_idx",
        edge_info_to_col="termination_region_idx",
        node_index_column="region_idx",
    )


def direct_connections(sex: Sex, region_id: str, node_as: NodeIs) -> pl.DataFrame:

    # Get index of node with 'name=region_name'
    connections = get_connections(sex)
    node_index = connections.node_indexes_from_information(
        pl.col("region_id") == region_id
    )
    if len(node_index) != 1:
        msg = f"Found {len(node_index)} nodes with name {region_id}"
        raise ValueError(msg)

    # Get names of nodes with direct connection
    directs = connections.direct_connections(
        node_internal_index=node_index[0], node_as=node_as
    )

    result_dfs = []
    for node_list, source in zip(directs, ["input", "output"], strict=True):
        node_df = connections.node_information_from_index(node_list).select("region_id")
        node_df = node_df.with_columns(pl.lit(source).alias("node_as"))
        result_dfs.append(node_df)

    return pl.concat(result_dfs)
