# -*- coding: utf-8 -*- #

from typing import Union
from ec2instances.ec2_instance_mapping import Ec2RemoteShellProxy
from pyclvm._common.gcp_instance_mapping import GcpRemoteShellProxy
from pyclvm._common.azure_instance_mapping import AzureRemoteShellProxy
from ._process import process_instances

# TODO move the getting platform out of here
platform = None


def _execute_aws(instance_name: str, instance: Ec2RemoteShellProxy, **kwargs) -> None:
    print(f"Working {instance_name} ...")
    instance.execute(kwargs.get("script"), **kwargs)


def _execute(
    instance_name: str,
    instance: Union[GcpRemoteShellProxy, AzureRemoteShellProxy],
    **kwargs,
) -> None:
    print(f"Working {instance_name} ...")
    instance.execute((kwargs.get("script"),), **kwargs)


def command(instance_name: str, script: str, **kwargs: str) -> None:
    """
    not implemented
    """
    kwargs["script"] = script

    global platform
    platform = kwargs.get("platform", "aws")

    if platform == "aws":
        process_instances(_execute_aws, "running", (instance_name,), kwargs)
    elif platform == "gcp":
        process_instances(_execute, "RUNNING", (instance_name,), kwargs)
    elif platform == "azure":
        process_instances(_execute, "VM running", (instance_name,), kwargs)
    else:
        raise RuntimeError("Unsupported platform")
