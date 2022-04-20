from pyclvm.ssm.session import start as start_session


def connect(instance_name: str, **kwargs: str) -> None:
    """
    connect to a Virtual Machine

    Args:
        instance_name (str): Virtual Machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None

    """
    start_session(instance_name, **kwargs)
