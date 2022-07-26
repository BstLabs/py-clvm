"""start/stop port redirection session"""

from typing import Dict, Tuple


def _get_port_mapping(kwargs: Dict) -> Tuple:
    if kwargs:
        try:
            port = kwargs.get("port", 8080)
            local_port = kwargs.get("local_port", 8080)
            return (int(port), int(local_port))
        except ValueError as err:
            raise Exception(
                "[INFO] Only integer type supported for port numbers!"
            ) from err
    return 8080, 8080


def _make_file_name(
    platform: str, profile: str, instance_name: str, port: int, local_port: int
) -> str:
    return f"{platform}-{profile}-{instance_name}-{port}={local_port}"


from .start import start
from .stop import stop

__all__ = ["start", "stop"]
