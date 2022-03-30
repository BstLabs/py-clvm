from pyclvm._common.session import get_session


def stop(session_id: str, **kwargs: str) -> None:
    """
    Terminate ssm session

    Args:
        session_id (str): SSM session ID
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None

    """
    session = get_session(kwargs)
    client = session.client("ssm")
    client.terminate_session(SessionId=session_id)
