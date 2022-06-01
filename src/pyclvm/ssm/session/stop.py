from ec2instances.common.session import get_session


def stop(identifier: str, **kwargs: str) -> None:
    """
    terminate ssm session

    Args:
        identifier (str): SSM session ID
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None

    """
    session = get_session(kwargs)
    client = session.client("ssm")
    if identifier.startswith("i-0"):  # close all sessions with a certain vm
        active_sessions = client.describe_sessions(
            State="Active", Filters=[{"key": "Target", "value": identifier}]
        )
        for session_id in (s["SessionId"] for s in active_sessions["Sessions"]):
            client.terminate_session(SessionId=session_id)
    else:  # close a single session
        client.terminate_session(SessionId=identifier)
