"""start/stop port redirection session"""

from typing import Tuple


def _get_port_mapping(**kwargs: str) -> Tuple[int, int]:
    if "port" in kwargs.keys():
        return int(kwargs["port"]), 8080
    elif "local_port" in kwargs.keys():
        return 8080, int(kwargs["local_port"])
    elif "port" and "local_port" in kwargs.keys():
        return int(kwargs["port"]), int(kwargs["local_port"])
    else:
        return 8080, 8080


def _make_file_name(
    platform: str, profile: str, instance_name: str, port: int, local_port: int
) -> str:
    return f"{platform}-{profile}-{instance_name}-{port}={local_port}"


from .start import start
from .stop import stop

__all__ = ["start", "stop"]
