"""start/stop port redirection session"""

from typing import Dict, Tuple


def _get_port_mapping(**kwargs: str) -> Tuple[int, int]:
    if kwargs:
        try:
            return 8080, int(kwargs.get("port", 8080))
        except ValueError as err:
            raise ValueError(
                "[INFO] Only integer type supported for port numbers!"
            ) from err
    return 8080, 8080


def _make_file_name(
    platform: str, profile: str, instance_name: str, local_port: int
) -> str:
    return f"{platform}-{profile}-{instance_name}-8080={local_port}"


from .start import start
from .stop import stop

__all__ = ["start", "stop"]
