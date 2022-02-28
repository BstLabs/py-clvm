from _ssm import start_session

def connect(name: str, **kwargs: str) -> None:
    """
    connect to a Virtual Machine

    Args:
        name (str): Virtual Machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None

    """
    start_session(name, **kwargs)

