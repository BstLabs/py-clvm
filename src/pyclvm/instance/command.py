# -*- coding: utf-8 -*- #

from typing import Dict, Union

from ec2instances.ec2_instance_proxy import Ec2InstanceProxy

from pyclvm._common.gcp_instance_mapping import GcpRemoteShellProxy
from pyclvm.plt import _default_platform, _unsupported_platform


def _execute_aws(instance_name: str, instance: Ec2InstanceProxy, **kwargs) -> None:
    print(f"Working {instance_name} ...")
    instance.execute(kwargs.get("script"), **kwargs)


def _execute_gcp(instance_name: str, instance: GcpRemoteShellProxy, **kwargs) -> None:
    print(f"Working {instance_name} ...")
    instance.execute((kwargs.get("script"),), **kwargs)


def _execute_azure(instance_name: str, **kwargs):
    ...


def command(instance_name: str, script: str, **kwargs) -> Union[Dict, None]:
    """
    not implemented
    """
    kwargs["script"] = script

    supported_platforms = {"AWS", "GCP", "AZURE"}
    platform = _default_platform(**kwargs)

    if platform in supported_platforms:
        return {
            "AWS": _execute_aws(instance_name, **kwargs),
            "GCP": _execute_gcp(instance_name, **kwargs),
            "AZURE": _execute_azure(instance_name, **kwargs),
        }
    else:
        _unsupported_platform(platform)
