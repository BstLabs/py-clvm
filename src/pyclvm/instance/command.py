# -*- coding: utf-8 -*- #
from functools import partial
from typing import Dict, Union

from ._process import process_instances

from ec2instances.ec2_instance_proxy import Ec2InstanceProxy

from pyclvm._common.gcp_instance_mapping import GcpRemoteShellProxy
from pyclvm._common.azure_instance_mapping import AzureRemoteShellProxy
from pyclvm.plt import _default_platform, _unsupported_platform


def _execute_aws(instance_name: str, instance: Ec2InstanceProxy, **kwargs) -> None:
    print(f"Working {instance_name} ...")
    instance.execute(kwargs.get("script"), **kwargs)


def _execute_gcp(instance_name: str, instance: GcpRemoteShellProxy, **kwargs) -> None:
    print(f"Working {instance_name} ...")
    instance.execute((kwargs.get("script"),), **kwargs)


def _execute_azure(
    instance_name: str, instance: AzureRemoteShellProxy, **kwargs
) -> None:
    print(f"Working {instance_name} ...")
    instance.execute((kwargs.get("script"),), **kwargs)


def command(instance_name: str, script: str, **kwargs: str) -> Union[Dict, None]:
    """
    not implemented
    """
    kwargs["script"] = script
    platform, supported_platforms = _default_platform(**kwargs)

    if platform in supported_platforms:
        return {
            "AWS": partial(
                process_instances, _execute_aws, "running", (instance_name,), kwargs
            ),
            "GCP": partial(
                process_instances, _execute_gcp, "RUNNING", (instance_name,), kwargs
            ),
            "AZURE": partial(
                process_instances,
                _execute_azure,
                "VM running",
                (instance_name,),
                kwargs,
            ),
        }[platform.upper()]()
    else:
        _unsupported_platform(platform)
