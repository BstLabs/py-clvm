import socket
from time import sleep
from jdict import jdict
from typing import Tuple
from _common.user_data import store
from _common.ssm import start_session
from . import _make_file_name

def start(instance_name: str, **kwargs: str) -> int:
    """
    start ssh tunnelling to a Virtual Machine

    Args:
        instance_name (str): Virtual Machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None
    """
    pid = start_session(
        instance_name, 
        '--document-name',
        'AWS-StartSSHSession',
        '--parameter',
        'portNumber=22',
        wait=False
    ).pid
    file_name = _make_file_name(
        'aws',
        kwargs.get('profile', 'default'),
        instance_name
    )
    store(file_name, jdict(pid=pid)) # TODO store session id and use terminate session
