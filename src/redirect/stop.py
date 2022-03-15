import psutil
from jdict import jdict
from typing import Tuple
from _common.user_data import fetch, remove
from . import _make_file_name, _get_port_mapping

def _kill_process_tree(pid: int) -> None:
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass

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
        _kill_process_tree(fetch(file_name).pid)
        remove(file_name)
    except FileNotFoundError:
        pass
    

    

