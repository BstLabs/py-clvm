import subprocess

from _common.session import get_session


def start(**kwargs: str) -> None:
    """
    obtain token, start instance if required, and launch vscode editor

    Args:
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None

    """
    get_session(kwargs)
    subprocess.Popen(args=["code"])
