from typing import Dict, Final, Tuple

import boto3
from ec2instances.ec2_instance_mapping import Ec2AllInstancesData
from rich.console import Console
from rich.table import Table


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
    current_profile = kwargs.get("profile", "")
    if current_profile:
        boto3.setup_default_session(profile_name=current_profile)

    instances = Ec2AllInstancesData()
    sts_client = boto3.client("sts")

    account = sts_client.get_caller_identity().Account
    table = Table(title=f"{account} Account EC2 Instances")
    for column in _COLUMNS:
        table.add_column(column, justify="left", no_wrap=True)

    for instance_id, instance_name, state_value, state_name in instances:
        table.add_row(
            *(
                instance_id,
                instance_name,
                f"[{_STATE_COLOR[state_value]}]{state_name}",
            )
        )

    console = Console()
    console.print(table)
