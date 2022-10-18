"""
start port(s) redirection to a Virtual Machine
"""

import json
import socket
from time import sleep
from typing import Optional

import psutil
from ec2instances.common.user_data import store
from jdict import jdict

from pyclvm.ssm.session import start as start_session

from . import _get_port_mapping, _make_file_name


def _wait_for_port(port: int) -> None:
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(("localhost", port))
        if result == 0:
            break
        sleep(10)


def _get_session_id(pid: int) -> Optional[str]:
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        cmd, args, *_ = child.cmdline()
        if cmd == "session-manager-plugin":
            return json.loads(args).SessionId


def start(instance_name: str, **kwargs: str) -> int:
    """
    start port(s) redirection to a Virtual Machine

    Args:
        instance_name (str): vm instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name and port numbers (default 8080=8080)

    Returns:
        local port number (int)

    """
    port, local_port = _get_port_mapping(**kwargs)
    pid = start_session(
        instance_name,
        "--document-name",
        "AWS-StartPortForwardingSession",
        "--parameters",
        f"portNumber={port},localPortNumber={local_port}",
        **kwargs,
        wait="False",
    ).pid
    _wait_for_port(local_port)
    session_id = _get_session_id(pid)
    file_name = _make_file_name(
        "aws", kwargs.get("profile", "default"), instance_name, local_port
    )
    store(file_name, jdict(pid=pid, session_id=session_id))
    print(
        f"[<!>] Click the link to redirect to browser: http://localhost:{local_port}/"
    )
    return local_port
