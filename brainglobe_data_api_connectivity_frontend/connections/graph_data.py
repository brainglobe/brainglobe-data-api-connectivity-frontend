from pathlib import Path

from brainglobe_data_api_connectivity.connections import Connections


def get_connections() -> Connections:
    data_dir = Path(__file__).parent / "data"

    return Connections.from_files(
        node_info=data_dir / "small-nodes.csv",
        edge_table=data_dir / "small-edge-table.csv",
        edge_info=data_dir / "small-edge-meta.csv",
    )
