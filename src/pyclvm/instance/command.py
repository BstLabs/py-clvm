# -*- coding: utf-8 -*- #
"""send system commands to VM"""

from functools import partial
from typing import Any, Tuple, Union

from ec2instances.ec2_instance_proxy import Ec2RemoteShellProxy

from pyclvm._common.azure_instance_mapping import AzureRemoteShellProxy
from pyclvm._common.gcp_instance_mapping import GcpRemoteShellProxy
from pyclvm.plt import (
    _default_platform,
    _get_supported_platforms,
    _unsupported_platform,
)

from ._process import process_instances


def _execute_aws(instance_name: str, instance: Ec2RemoteShellProxy, **kwargs) -> None:
    print(f"Working {instance_name} ...")
    instance.start()
    # to get rid of the overloading warning script assigned to a variable
    script = kwargs.pop("script")
    # custom script ensures that the pwd is ssm-user
    custom_script = f"cd /home/ssm-user && {script}"
    instance.execute(custom_script, **kwargs)


def _execute_gcp(instance_name: str, instance: GcpRemoteShellProxy, **kwargs) -> None:
    print(f"Starting {instance_name} ...")
    instance.start()
    print(f"{instance_name} is running")
    print(f"Working {instance_name} ...")

    instance.execute((f"cd $HOME && {kwargs.get('script')}",), **kwargs)


def _execute_azure(
    instance_name: str, instance: AzureRemoteShellProxy, **kwargs
) -> None:
    print(f"Starting {instance_name} ...")
    instance.start(wait=False)
    print(f"{instance_name} is running")
    print(f"Working {instance_name} ...")

    instance.execute((kwargs.get("script"),), **kwargs)


def command(
    instance_name: str, script: str, **kwargs: str
) -> Union[Tuple[Any, str], None]:
    """
    send system commands to VM

    Args:
        instance_name (str): vm instance name
        script (str): system commands wrapped around " "
        **kwargs (str): (optional) additional arguments, currently only profile

    Returns:
        Union[Tuple[Any, str], None]
    """
    kwargs["script"] = script
    default_platform, supported_platforms = (
        _default_platform(**kwargs),
        _get_supported_platforms(),
    )

    if default_platform in supported_platforms:
        return {
            "AWS": partial(
                process_instances, _execute_aws, "running", (instance_name,), **kwargs
            ),
            "GCP": partial(
                process_instances, _execute_gcp, "RUNNING", (instance_name,), **kwargs
            ),
            "AZURE": partial(
                process_instances,
                _execute_azure,
                "VM running",
                (instance_name,),
                **kwargs,
            ),
        }[default_platform.upper()]()
    _unsupported_platform(default_platform)
