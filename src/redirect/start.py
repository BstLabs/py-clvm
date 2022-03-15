import socket
from time import sleep
from jdict import jdict
from typing import Tuple
from _common.user_data import store
from _common.ssm import start_session
from . import _make_file_name, _get_port_mapping

def _wait_for_port(port: int) -> None:
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        if result == 0:
            break
        sleep(10)

def start(instance_name: str, **kwargs: str) -> int:
    """
    start port(s) redirection to a Virtual Machine

    Args:
        instance_name (str): Virtual Machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name and port numbers (default 8080=8080)

    Returns:
        local port number (int)

    """
    port, local_port = _get_port_mapping(kwargs)
    pid = start_session(
        instance_name, 
        '--document-name',
        'AWS-StartPortForwardingSession',
        '--parameters',
        f'portNumber={port},localPortNumber={local_port}',
        **kwargs,
        wait=False
    ).pid
    _wait_for_port(local_port)
    file_name = _make_file_name(
        'aws',
        kwargs.get('profile', 'default'),
        instance_name,
        port,
        local_port
    )
    store(file_name, jdict(pid=pid))
    return local_port
    
