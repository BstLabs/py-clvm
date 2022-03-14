import psutil
from jdict import jdict
from typing import Tuple
from _common.user_data import fetch, remove
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
    file_name = _make_file_name(
        'aws',
        kwargs.get('profile', 'default'),
        instance_name,
        port,
        local_port
    )
    pid = fetch(file_name).pid
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        child.kill()
    parent.kill()
    remove(file_name)
    

