import os
import subprocess
from typing import Any, List

from ec2instances.ec2_instance_mapping import Ec2RemoteShellMapping

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
    _run_subprocess(instance_name, _get_path(**kwargs), _platform)
    _get_platform_instance(instance_name, _platform, **kwargs)().start()


def _get_vscode_cmd(instance_name: str, path: str, _platform: str) -> List[str]:
    return [
        "code",
        "--folder-uri",
        f"vscode-remote://ssh-remote+{instance_name}-{_platform.lower()}{path}",
    ]


def _run_subprocess(instance_name: str, path: str, _platform: str) -> None:
    cmd = _get_vscode_cmd(instance_name, path, _platform)
    process = subprocess.Popen(args=cmd)
    process.communicate()
    os.environ["VSCODE_AWS_PROMPT"] = "True"


def _get_path(**kwargs: str) -> str:
    return kwargs.get("path", "/home")


def _get_platform_instance(instance_name: str, _platform: str, **kwargs: str) -> Any:
    platform_instance_map = {
        "AWS": lambda: Ec2RemoteShellMapping(get_session(kwargs)).get(instance_name),
        "GCP": lambda: GcpRemoteShellMapping().get(instance_name),
        "AZURE": lambda: AzureRemoteShellMapping().get(instance_name),
    }
    return platform_instance_map.get(_platform.upper())
