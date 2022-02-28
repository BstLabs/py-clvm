import subprocess
from _ssm import start_session
from typing import Tuple

def _get_port_mapping(kwargs: dict) -> tuple:
    for port, localPort in kwargs.items():
        try:
            int(port)
            int(localPort)
            return port, localPort
        except ValueError:
            pass
    return "8080", "8080"

def redirect_port(name: str, **kwargs: str) -> Tuple[subprocess.Popen, str]:
    port, localPort = _get_port_mapping(kwargs)
    return start_session(
        name, 
        '--document-name',
        'AWS-StartPortForwardingSession',
        '--parameters',
        f'portNumber={port},localPortNumber={localPort}',
        **kwargs
    ), port

def redirect(name: str, **kwargs: str) -> None:
    """
    redirect ports to a Virtual Machine

    Args:
        name (str): Virtual Machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name and port numbers (default 8080=8080)

    Returns:
        None

    """
    redirect_port(name, **kwargs)
    

