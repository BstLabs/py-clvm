from pyclvm.ssm.session.start import start as start_session
from time import sleep

from pyclvm._common.azure_instance_mapping import (
    AzureRemoteShellMapping,
    AzureRemoteShellProxy,
)
from pyclvm._common.azure_instance_proxy import (
    AzureRemoteConnector,
    TcpProxy
)

# TODO move the getting platform out of here
target_platform = None

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

    global target_platform
    target_platform = kwargs.get("platform", "aws")

    if target_platform == "aws":
        return _start_aws(instance_name, port, **kwargs)
    elif target_platform == "gcp":
        return _start_gcp(instance_name, port, **kwargs)
    elif target_platform == "azure":
        return _start_azure(instance_name, port, **kwargs)
    else:
        raise RuntimeError("Unsupported platform")


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
    tunnel = AzureRemoteConnector(instance, port)
    tunnel.start()
    sleep(5)
    TcpProxy('127.0.0.1', port)()
    tunnel.join()
