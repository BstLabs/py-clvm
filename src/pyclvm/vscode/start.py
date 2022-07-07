import subprocess
from functools import partial

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
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None

    """
    platform, supported_platforms = _default_platform(**kwargs)

    if platform in supported_platforms:
        return {
            "AWS": partial(_start_aws, instance_name, platform, **kwargs),
            "GCP": partial(_start_gcp, instance_name, platform, **kwargs),
            "AZURE": partial(_start_azure, instance_name, platform, **kwargs),
        }[platform.upper()]()
    else:
        _unsupported_platform(platform)


# ---
def _start_aws(instance_name: str, _platform: str, **kwargs: str) -> None:
    instance = Ec2RemoteShellMapping(get_session(kwargs)).get(instance_name)
    instance.start()

    path = kwargs.get("path", "/home/ssm-user")
    cmd = [
        "code",
        "--folder-uri",
        f"vscode-remote://ssh-remote+{instance_name}-{_platform.lower()}{path}",
    ]
    subprocess.Popen(args=cmd, shell=True)


# ---
def _start_gcp(instance_name: str, _platform: str, **kwargs: str) -> None:
    instance = GcpRemoteShellMapping().get(instance_name)
    instance.start()

    path = kwargs.get("path", "/home")
    cmd = [
        "code",
        "--folder-uri",
        f"vscode-remote://ssh-remote+{instance_name}-{_platform.lower()}{path}",
    ]
    subprocess.Popen(args=cmd, shell=True)


# ---
def _start_azure(instance_name: str, _platform: str, **kwargs: str) -> None:
    instance = AzureRemoteShellMapping().get(instance_name)
    instance.start()

    path = kwargs.get("path", "/home")
    cmd = [
        "code",
        "--folder-uri",
        f"vscode-remote://ssh-remote+{instance_name}-{_platform.lower()}{path}",
    ]
    subprocess.Popen(args=cmd, shell=True)
