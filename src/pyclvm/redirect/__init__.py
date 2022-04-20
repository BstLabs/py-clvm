"""start/stop port redirection session"""

import contextlib


def _get_port_mapping(kwargs: dict) -> tuple:
    for port, local_port in kwargs.items():
        with contextlib.suppress(ValueError):
            return int(port), int(local_port)
    return 8080, 8080


def _make_file_name(
    platform: str, profile: str, instance_name: str, port: int, local_port: int
) -> str:
    return f"{platform}-{profile}-{instance_name}-{port}={local_port}"


from .start import start
from .stop import stop

__all__ = ["start", "stop"]
