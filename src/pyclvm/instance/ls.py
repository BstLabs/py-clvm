from typing import Dict, Final, Tuple, Union, List, Any

from _common.session_aws import get_session as aws_get_session

from _common.session_azure import get_session as azure_get_session
from ec2instances.ec2_instance_mapping import Ec2AllInstancesData
from rich.console import Console
from rich.table import Table


from _common.gcp_instance_mapping import GcpComputeAllInstancesData
from login.aws import aws as login_aws
from plt import (
    _default_platform,
    _get_supported_platforms,
    _unsupported_platform,
)

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

_COLUMNS: Final[Tuple[str, ...]] = ("Id", "Name", "Status")


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
            "AWS": _ls_aws,
            "GCP": _ls_gcp,
            "AZURE": _ls_azure,
        }[default_platform.upper()](**kwargs)
    else:
        _unsupported_platform(default_platform)



def _print_table(title: str, rows: List[Any]):
    """
    Prints the report table

    Args:
        title (str): the title on the top of the printed table
        rows (list): the renderable list of row data
    Returns:
        None
    """
    final_report_table = Table(title=title)
    for column in _COLUMNS:
        final_report_table.add_column(column, justify="left", no_wrap=True)

    for row in rows:
        final_report_table.add_row(*row)

    console = Console()
    console.print(final_report_table)


def _ls_aws(**kwargs: str) -> None:
    """
    list vm instances of AWS Cloud Platform

    Args:
        **kwargs (str): (optional) classifiers, at the moment, profile name, instance state, name patterns

    Returns:
        None

    """
    current_session = aws_get_session(**kwargs)
    instances = Ec2AllInstancesData(auth_callback=login_aws)
    title = f"\n\n{current_session.client('sts').get_caller_identity().Account}" \
            f" Account EC2 Instances" \
            f"\nprofile: {kwargs.get('profile', 'default')}\n"
    rows = []
    for instance_id, instance_name, state_value, state_name in instances:
        rows.append(
            (
                instance_id,
                instance_name,
                f"[{_STATE_COLOR[state_value]}]{state_name}",
            )
        )
    _print_table(title, rows)



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
    title = f"\n\n{instances.get_session().account_email} Account GCP Instances" \
            f"\nprofile: {kwargs.get('profile', 'default')}\n"
    rows = []
    for instance_id, instance_name, state in instances:
        rows.append(
            (
                str(instance_id),
                instance_name,
                f"[{_STATE_COLOR_GCP[state]}]{state}",
            )
        )
    _print_table(title, rows)


# ---
def _ls_azure(**kwargs: str) ->None:
    """
    list vm instances of Azure Cloud Platform

    Args:
        **kwargs (str): (optional) classifiers, at the moment, profile name, instance state, name patterns

    Returns:
        None

    """
    _session = azure_get_session()
    title = f"\n\n{_session.subscription_name} Azure Instances" \
            f"\nprofile: {kwargs.get('profile', 'default')}\n"
    rows = []
    for instance, params in _session.instances.items():
        rows.append(
            (
                str(params["instance_id"]),
                instance,
                f"[{_STATE_COLOR_AZURE[params['state']]}]{params['state']}",
            )
        )
    _print_table(title, rows)
