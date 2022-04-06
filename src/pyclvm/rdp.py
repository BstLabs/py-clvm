import subprocess
import time
from distutils.log import warn
from sys import platform
from typing import Dict, Final, Tuple

from pyclvm import redirect

_SYSTEM_RDP_CLIENT: Final[Dict[str, Tuple[str, ...]]] = {
    "win32": (),
    "linux": (
        "xfreerdp",
        "/dynamic-resolution",
        "+toggle-fullscreen",
        "/v:localhost:{local_port}",
    ),
    "darwin": (
        "/Applications/Microsoft Remote Desktop.app/Contents/MacOS/Microsoft Remote Desktop",
        ">",
        "/dev/null",
        "2>&1",
    ),
}
_RDP_PORT: Final[str] = "3389"


def rdp(instance_name: str, **kwargs: str) -> None:
    """
    redirect ports to a Virtual Machine and launch rdp session

    Args:
        instance_name (str): Virtual Machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name and port numbers (default 8080=8080)

    Returns:
        None

    """
    cmd = _SYSTEM_RDP_CLIENT[platform]
    if not cmd:
        raise SystemError(f"RDP client not configured for {platform=}")
    # start port redirection
    if _RDP_PORT not in kwargs:
        kwargs[_RDP_PORT] = _RDP_PORT
    local_port = redirect.start(instance_name, **kwargs)

    # launch rdp
    if platform == "darwin":
        warn(
            "\nCreate profile connection manually, server: localhost, port: 3389, or copy link rdp://localhost:3389\n"
        )
        time.sleep(10)

    subprocess.run([s.format(local_port=local_port) for s in cmd])

    # stop port redirection
    redirect.stop(instance_name, **kwargs)

