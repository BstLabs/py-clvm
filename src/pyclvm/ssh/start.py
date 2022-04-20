from pyclvm.ssm.session import start as start_session


def start(instance_name: str, port: int, **kwargs: str) -> None:
    """
    start ssh tunnelling to a Virtual Machine

    Args:
        instance_name (str): Virtual Machine instance name
        port (int): port number
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None
    """
    start_session(
        instance_name,
        "--document-name",
        "AWS-StartSSHSession",
        "--parameter",
        f"portNumber={port}",
        wait=True,
        **kwargs,
    )
