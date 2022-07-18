import subprocess
from typing import List

from ec2instances.ec2_instance_mapping import Ec2RemoteShellMapping

from pyclvm._common.azure_instance_mapping import AzureRemoteShellMapping
from pyclvm._common.gcp_instance_mapping import GcpRemoteShellMapping
from pyclvm._common.session import get_session
from pyclvm.plt import _default_platform, _unsupported_platform


def start(instance_name: str, **kwargs: str) -> None:
    """
    obtain token, start instance if required, and launch vscode editor

    Args:
        instance_name (str): Virtual Machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name and path
    Returns:
        None

    """
    platform, supported_platforms = _default_platform(**kwargs)

    if platform in supported_platforms:
        return _start_vscode_with_given_platform(instance_name, platform, **kwargs)
    else:
        _unsupported_platform(platform)


def _start_vscode_with_given_platform(
    instance_name: str, _platform: str, **kwargs: str
) -> None:
    _get_platform_instance(instance_name, _platform, **kwargs)().start()
    _run_subprocess(instance_name, _get_path(**kwargs), _platform)


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


def _get_path(**kwargs: str) -> str:
    return kwargs.get("path", "/home")


def _get_platform_instance(
    instance_name: str, _platform: str, **kwargs: str
) -> callable:
    platform_instance_map = {
        "AWS": lambda: Ec2RemoteShellMapping(get_session(kwargs)).get(instance_name),
        "GCP": lambda: GcpRemoteShellMapping().get(instance_name),
        "AZURE": lambda: AzureRemoteShellMapping().get(instance_name),
    }
    return platform_instance_map.get(_platform.upper())
