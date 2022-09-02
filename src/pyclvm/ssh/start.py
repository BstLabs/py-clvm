import subprocess
from functools import partial

from pyclvm._common.azure_instance_mapping import AzureRemoteShellMapping
from pyclvm._common.azure_instance_proxy import AzureRemoteConnector, AzureRemoteSocket
from pyclvm._common.gcp_instance_mapping import GcpRemoteShellMapping
from pyclvm.plt import (
    _default_platform,
    _get_os,
    _get_supported_platforms,
    _unsupported_platform,
)
from pyclvm.ssm.session.start import start as start_session

_OS = _get_os()


def start(instance_name: str, port: int, **kwargs: str) -> None:
    """
    start ssh tunnelling to a virtual machine

    Args:
        instance_name (str): Virtual Machine instance name
        port (int): port number
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None
    """
    default_platform, supported_platforms = (
        _default_platform(**kwargs),
        _get_supported_platforms(),
    )

    if default_platform in supported_platforms:
        return {
            "AWS": partial(_start_aws, instance_name, port, **kwargs),
            "GCP": partial(_start_gcp, instance_name, port, **kwargs),
            "AZURE": partial(_start_azure, instance_name, port, **kwargs),
        }[default_platform.upper()]()
    _unsupported_platform(default_platform)


def _start_aws(instance_name: str, port: int, **kwargs: str) -> None:
    start_session(
        instance_name,
        "--document-name",
        "AWS-StartSSHSession",
        "--parameter",
        f"portNumber={port}",
        wait=True,
        **kwargs,
    )


def _start_gcp(instance_name: str, **kwargs: str) -> None:
    instance = GcpRemoteShellMapping(**kwargs).get(instance_name)

    print(f"Starting {instance_name} ...")
    instance.start()
    print(f"\n{instance_name} is running")

    cmd = [
        "gcloud.cmd" if _OS == "Windows" else "gcloud",
        "compute",
        "start-iap-tunnel",
        instance_name,
        "22",
        "--listen-on-stdin",
        f"--project={instance.session.project}",
        f"--zone={instance.session.zone}",
        "--verbosity=warning",
    ]
    subprocess.run(cmd, check=True)


def _start_azure(instance_name: str, port: int, **kwargs: str) -> None:
    instance = AzureRemoteShellMapping().get(instance_name)

    print(f"Starting {instance_name} ...")
    instance.start()
    print(f"\n{instance_name} is running")

    connector = AzureRemoteConnector(instance, port, **kwargs)
    socket = AzureRemoteSocket(instance, connector, port, **kwargs)
    connector.start()
    socket.start()
    connector.join()
    socket.join()
