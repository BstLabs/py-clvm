from typing import Dict, Final, Tuple

import boto3
from ec2instances.ec2_instance_mapping import Ec2AllInstancesData
from rich.console import Console
from rich.table import Table

from pyclvm._common.gcp_instance_mapping import GcpComputeAllInstancesData

_COLUMNS: Final[Tuple[str, ...]] = ("Id", "Name", "Status")

_STATE_COLOR: Final[Dict[int, str]] = {
    0: "bright_yellow",
    16: "bright_green",
    32: "yellow",
    48: "red",
    64: "bright_magneta",
    80: "bright_red",
}

_STATE_COLOR_GCP: Final[Dict[str, str]] = {
    "DEPROVISIONING": "dark_orange",
    "PROVISIONING": "orange1",
    "REPAIRING": "yellow2",
    "RUNNING": "bright_green",
    "STAGING": "yellow1",
    "STOPPED": "gold3",
    "STOPPING": "misty_rose3",
    "SUSPENDED": "bright_magenta",
    "SUSPENDING": "orchid",
    "TERMINATED": "red",
    "UNDEFINED_STATUS": "bright_red",
}


def ls(**kwargs: str) -> None:
    """
    list vm instances

    Args:
        **kwargs (str): (optional) classifiers, at the moment, profile name, instance state, name patterns

    Returns:
        None

    """
    platform = kwargs.get("platform", "aws")
    if platform == "aws":
        _ls_aws(**kwargs)
    elif platform == "gcp":
        _ls_gcp(**kwargs)
    elif platform == "azure":
        pass
    else:
        raise RuntimeError("Unsupported platform")


def _ls_aws(**kwargs: str) -> None:
    """
    list vm instances of AWS Cloud Platform

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


# ---
def _ls_gcp(**kwargs: str) -> None:
    """
    list vm instances of Google Cloud Platform

    Args:
        **kwargs (str): (optional) classifiers, at the moment, profile name, instance state, name patterns

    Returns:
        None

    """
    instances = GcpComputeAllInstancesData(**kwargs)
    table = Table(title=f"{instances.session.account_email} Account GCP Instances")
    for column in _COLUMNS:
        table.add_column(column, justify="left", no_wrap=True)

    for instance_id, instance_name, state in instances:
        table.add_row(
            *(
                str(instance_id),
                instance_name,
                f"[{_STATE_COLOR_GCP[state]}]{state}",
            )
        )

    console = Console()
    console.print(table)
