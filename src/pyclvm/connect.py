from pyclvm.ssm.session import start as start_session


def connect(instance_name: str, **kwargs: str) -> None:
    """
    connect to a virtual machine

    Args:
        instance_name (str): virtual machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None

    """
    start_session(instance_name, **kwargs)
