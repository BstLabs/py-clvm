import os
import subprocess
import sys
from functools import partial
from pathlib import Path
from time import sleep

from pyclvm._common.azure_instance_mapping import AzureRemoteShellMapping
from pyclvm._common.azure_instance_proxy import AzureRemoteConnector, AzureRemoteSocket
from pyclvm._common.gcp_instance_mapping import GcpRemoteShellMapping
from pyclvm.plt import (
    _default_platform,
    _get_supported_platforms,
    _unsupported_platform,
)
from pyclvm.ssm.session.start import start as start_session

from pyclvm.plt import _get_os

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
    else:
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


def _start_gcp(instance_name: str, port: int, **kwargs: str) -> None:
    instance = GcpRemoteShellMapping().get(instance_name)

    pre_state = instance.state

    print(f"Starting {instance_name} ...")
    instance.start()
    if pre_state != "RUNNING":
        sleep(15)
    print(f"{instance_name} is running")

    # sdk_name = "google-cloud-sdk"
    # cli_name = "google-cloud-cli"
    # current_dir = str(Path(os.path.dirname(os.path.realpath(__file__))).resolve())
    # possible_location_prefixes = [
    #     # -- current dir
    #     f"{current_dir}/{sdk_name}/lib/",
    #     f"{current_dir}/{cli_name}/lib/",
    #     # -- standard Linux
    #     f"/usr/lib/{sdk_name}/lib/",
    #     f"/usr/lib/{cli_name}/lib/",
    #     # -- Windows
    #     f"{os.getenv('PROGRAMFILES(x86)', '')}\\Google\\Cloud SDK\\lib\\",
    #     f"{os.getenv('PROGRAMFILES(x86)', '')}\\Google\\Cloud CLI\\lib\\",
    #     # -- standard Darwin
    #     f"{os.getenv('HOME')}/{sdk_name}/lib/",
    #     f"{os.getenv('HOME')}/{cli_name}/lib/",
    #     # -- snap
    #     f"/snap/{sdk_name}/current/lib/",
    #     f"/snap/{cli_name}/current/lib/",
    # ]
    #
    # gcloud_path = ""
    #
    # for possible_location_prefix in possible_location_prefixes:
    #     if os.path.isdir(possible_location_prefix):
    #         gcloud_path = f"{possible_location_prefix}gcloud.py"
    #         break
    #
    # if not gcloud_path.strip():
    #     print("Install Google CLoud Platform CLI or SDK")
    #     sys.exit(-1)

    cmd = [
        # "python3",
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
    subprocess.run(cmd)


def _start_azure(instance_name: str, port: int, **kwargs: str) -> None:
    instance = AzureRemoteShellMapping().get(instance_name)
    pre_state = instance.state

    print(f"Starting {instance_name} ...")
    instance.start()
    if pre_state != "VM running":
        sleep(15)
    print(f"{instance_name} is running")

    connector = AzureRemoteConnector(instance, port)
    socket = AzureRemoteSocket(instance, connector, port)
    connector.start()
    socket.start()
    connector.join()
    socket.join()
