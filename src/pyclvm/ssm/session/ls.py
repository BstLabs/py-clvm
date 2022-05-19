from typing import Final, Tuple

from ec2instances.common.session import get_session
from rich.console import Console
from rich.table import Table

_COLUMNS: Final[Tuple[str, ...]] = ("SessionId", "Target", "DocumentName", "Owner")


def ls(**kwargs: str) -> None:
    """

    list all ssm session


    Args:
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None

    """
    session = get_session(kwargs)
    ssm_client = session.client("ssm")
    sts_client = session.client("sts")

    account = sts_client.get_caller_identity().Account
    table = Table(title=f"{account} Account SSM Sessions")
    for column in _COLUMNS:
        table.add_column(column, justify="left", no_wrap=True)

    response = ssm_client.describe_sessions(State="Active")
    for session in response.Sessions:
        table.add_row(*(session.get(column, "") for column in _COLUMNS))

    console = Console()
    console.print(table)
