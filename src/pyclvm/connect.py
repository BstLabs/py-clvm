# -*- coding: utf-8 -*- #

from pyclvm.ssm.session import start as start_session
from typing import Union

from instance._process import process_instances
from pyclvm._common.gcp_instance_mapping import GcpRemoteShellProxy
from pyclvm._common.azure_instance_mapping import AzureRemoteShellProxy


# TODO move the getting platform out of here
platform = None


# ---
def _connect(instance_name: str, instance: Union[GcpRemoteShellProxy, AzureRemoteShellProxy], **kwargs) -> None:
    print(f"Connecting to {instance_name} ...")
    instance.execute((), **kwargs)


def connect(instance_name: str, **kwargs: str) -> None:
    """
    connect to a virtual machine

    Args:
        instance_name (str): virtual machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None

    """
    global platform
    platform = kwargs.get("platform", "aws")

    if platform == "aws":
        start_session(instance_name, **kwargs)
    elif platform == "gcp":
        process_instances(_connect, "RUNNING", (instance_name,), kwargs)
    elif platform == "azure":
        process_instances(_connect, "VM running", (instance_name,), kwargs)
    else:
        raise RuntimeError("Unsupported platform")
