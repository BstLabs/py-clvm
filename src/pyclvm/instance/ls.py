from typing import Dict, Final, Tuple

from rich.console import Console
from rich.table import Table

from pyclvm._common.session import get_session

from ._mapping import InstanceMapping

_COLUMNS: Final[Tuple[str, ...]] = ("Id", "Name", "Status")

_STATE_COLOR: Final[Dict[int, str]] = {
    0: "bright_yellow",
    16: "bright_green",
    32: "yellow",
    48: "red",
    64: "bright_magneta",
    80: "bright_red",
}


def ls(**kwargs: str) -> None:
    """
    list vm instances

    Args:
        **kwargs (str): (optional) classifiers, at the moment, profile name, instance state, name patterns

    Returns:
        None

    """
    instances = InstanceMapping(**kwargs)
    session = get_session(kwargs)
    sts_client = session.client("sts")

    account = sts_client.get_caller_identity().Account
    table = Table(title=f"{account} Account EC2 Instances")
    for column in _COLUMNS:
        table.add_column(column, justify="left", no_wrap=True)

    for name, instance in instances.items():
        table.add_row(
            *(
                instance.id,
                name,
                f"[{_STATE_COLOR[instance.state.Code]}]{instance.state.Name}",
            )
        )

    console = Console()
    console.print(table)
