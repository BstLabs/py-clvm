from functools import partial
from typing import Dict, Final, Tuple, Union

import boto3
from _common.session_azure import get_session as azure_get_session
from ec2instances.ec2_instance_mapping import Ec2AllInstancesData
from rich.console import Console
from rich.table import Table

from pyclvm._common.gcp_instance_mapping import GcpComputeAllInstancesData
from pyclvm.login import _login_aws
from pyclvm.plt import (
    _default_platform,
    _get_supported_platforms,
    _unsupported_platform,
)

_COLUMNS: Final[Tuple[str, ...]] = ("Id", "Name", "Status")

# --- The list of colours of "rich"
# https://rich.readthedocs.io/en/stable/appendix/colors.html

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

_STATE_COLOR_AZURE: Final[Dict[str, str]] = {
    "VM starting": "dark_orange",
    "VM running": "bright_green",
    "VM stopping": "yellow1",
    "VM stopped": "gold3",
    "VM deallocating": "bright_magenta",
    "VM deallocated": "red",
    "Provisioning succeeded": "bright_red",
}


def ls(**kwargs: str) -> Union[Dict, None]:
    """
    list vm instances

    Args:
        **kwargs (str): (optional) classifiers, at the moment, profile name, instance state, name patterns

    Returns:
        None

    """
    default_platform, supported_platforms = (
        _default_platform(**kwargs),
        _get_supported_platforms(),
    )
    if default_platform in supported_platforms:
        return {
            "AWS": partial(_ls_aws, **kwargs),
            "GCP": partial(_ls_gcp, **kwargs),
            "AZURE": partial(_ls_azure, **kwargs),
        }[default_platform.upper()]()
    else:
        _unsupported_platform(default_platform)


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

    instances = Ec2AllInstancesData(auth_callback=_login_aws)
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
    table = Table(
        title=f"{instances.get_session().account_email} Account GCP Instances"
    )
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


# ---
def _ls_azure(**kwargs: str) -> None:
    """
    list vm instances of Azure Cloud Platform

    Args:
        **kwargs (str): (optional) classifiers, at the moment, profile name, instance state, name patterns

    Returns:
        None

    """
    _session = azure_get_session()

    table = Table(title=f"{_session.subscription_name} Azure Instances")
    for column in _COLUMNS:
        table.add_column(column, justify="left", no_wrap=True)

    for instance, params in _session.instances.items():
        table.add_row(
            *(
                str(params["instance_id"]),
                instance,
                f"[{_STATE_COLOR_AZURE[params['state']]}]{params['state']}",
            )
        )
    console = Console()
    console.print(table)
