import instance
from _common.user_data import fetch, remove
from ssm.session import stop as terminate_session
from . import _make_file_name, _get_port_mapping


def stop(instance_name: str, **kwargs: str) -> None:
    """
    stop port(s) redirection to a Virtual Machine

    Args:
        instance_name (str): Virtual Machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name and port numbers (default 8080=8080)

    Returns:
        None

    """
    port, local_port = _get_port_mapping(kwargs)
    try:
        file_name = _make_file_name(
            'aws',
            kwargs.get('profile', 'default'),
            instance_name,
            port,
            local_port
        )
        terminate_session(fetch(file_name).session_id, **kwargs)
        remove(file_name)
    except FileNotFoundError:
        pass

    # stop instance unless required to keep
    if not kwargs.get('keep_instance', False):
        instance.stop(instance_name, **kwargs)
