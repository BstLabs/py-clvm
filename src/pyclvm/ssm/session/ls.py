from typing import Final, Tuple

from _common.session import get_session
from rich.console import Console
from rich.table import Table

_COLUMNS: Final[Tuple[str, ...]] = ("SessionId", "Target", "DocumentName", "Owner")


def ls(**kwargs: str) -> None:
    """
    Terminate ssm session

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
    for c in _COLUMNS:
        table.add_column(c, justify="left", no_wrap=True)

    response = ssm_client.describe_sessions(State="Active")
    for session in response.Sessions:
        table.add_row(*(session.get(c, "") for c in _COLUMNS))

    console = Console()
    console.print(table)
