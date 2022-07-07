from functools import partial

from pyclvm._common.azure_instance_mapping import AzureRemoteShellMapping
from pyclvm._common.azure_instance_proxy import AzureRemoteConnector, AzureRemoteSocket
from pyclvm.plt import _default_platform, _unsupported_platform
from pyclvm.ssm.session.start import start as start_session


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
    platform, supported_platforms = _default_platform(**kwargs)

    if platform in supported_platforms:
        return {
            "AWS": partial(_start_aws, instance_name, port, **kwargs),
            "GCP": partial(_start_gcp, instance_name, port, **kwargs),
            "AZURE": partial(_start_azure, instance_name, port, **kwargs),
        }[platform.upper()]()
    else:
        _unsupported_platform(platform)


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


def _start_gcp(instance_name: str, port: int, **kwargs: str) -> None:
    print("Not implemented")


def _start_azure(instance_name: str, port: int, **kwargs: str) -> None:
    instance = AzureRemoteShellMapping().get(instance_name)
    connector = AzureRemoteConnector(instance, port)
    socket = AzureRemoteSocket(instance, connector, port)
    connector.start()
    socket.start()
    connector.join()
    socket.join()
