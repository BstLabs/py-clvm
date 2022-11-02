import subprocess
from time import sleep
from typing import Any, List

import psutil
from ec2instances.ec2_instance_mapping import Ec2RemoteShellMapping
from plt import _get_os

from pyclvm._common.azure_instance_mapping import AzureRemoteShellMapping
from pyclvm._common.gcp_instance_mapping import GcpRemoteShellMapping
from pyclvm._common.session_aws import get_session
from pyclvm.plt import (
    _default_platform,
    _get_supported_platforms,
    _unsupported_platform,
)


def start(instance_name: str, **kwargs: str) -> None:
    """
    obtain token, start instance if required, and launch vscode editor

    Args:
        instance_name (str): Virtual Machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name and path
    Returns:
        None

    """
    default_platform, supported_platforms = (
        _default_platform(**kwargs),
        _get_supported_platforms(),
    )

    if default_platform in supported_platforms:
        return _start_vscode_with_given_platform(
            instance_name, default_platform, **kwargs
        )
    else:
        _unsupported_platform(default_platform)


def _start_vscode_with_given_platform(
    instance_name: str, _platform: str, **kwargs: str
) -> None:
    _run_subprocess(instance_name, _platform, **kwargs)


def _get_vscode_cmd(instance_name: str, path: str, _platform: str) -> List[str]:
    return [
        "code.cmd" if "Windows" == _get_os() else "code",
        "--folder-uri",
        f"vscode-remote://ssh-remote+{instance_name}-{_platform.lower()}{path}",
    ]


def _run_subprocess(instance_name: str, _platform: str, **kwargs: str) -> None:
    cmd = _get_vscode_cmd(
        instance_name=instance_name,
        path=kwargs.get("path", "/home"),
        _platform=_platform,
    )
    vscode_proc_pid = subprocess.Popen(args=cmd).pid
    sleep(120)  # 2 minutes timeout for switching directory at start
    try:
        ssh_proc = next(
            p
            for p in psutil.process_iter()
            if p.pid > vscode_proc_pid
            and "ssh" in p.name()
            and next(cl for cl in p.cmdline() if instance_name in cl)
        )
        while psutil.pid_exists(ssh_proc.pid):
            sleep(1)
        _get_platform_instance(
            instance_name=instance_name, _platform=_platform, **kwargs
        ).stop(wait=False)
    except StopIteration:
        return


def _get_platform_instance(instance_name: str, _platform: str, **kwargs: str) -> Any:
    platform_instance_map = {
        "AWS": lambda: Ec2RemoteShellMapping(get_session(kwargs)).get(instance_name),
        "GCP": lambda: GcpRemoteShellMapping().get(instance_name),
        "AZURE": lambda: AzureRemoteShellMapping().get(instance_name),
    }
    return platform_instance_map.get(_platform.upper())()
