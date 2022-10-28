# -*- coding: utf-8 -*- #

from functools import partial
from typing import Dict, Union

from pyclvm._common.azure_instance_mapping import AzureRemoteShellProxy
from pyclvm._common.gcp_instance_mapping import GcpRemoteShellProxy
from pyclvm.instance._process import process_instances
from pyclvm.plt import (
    _default_platform,
    _get_supported_platforms,
    _unsupported_platform,
)
from pyclvm.ssm.session import start as start_session


# ---
def _connect(
    instance_name: str,
    instance: Union[GcpRemoteShellProxy, AzureRemoteShellProxy],
    **kwargs,
) -> None:
    print(f"Starting {instance_name} ...")
    instance.start(wait=False)
    print(f"{instance_name} is running")

    print(f"Connecting to {instance_name} ...")
    instance.execute((), **kwargs)


def connect(instance_name: str, **kwargs: str) -> Union[Dict, None]:
    """
    connect to a virtual machine

    Args:
        instance_name (str): virtual machine instance name
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
            "AWS": partial(start_session, instance_name, **kwargs),
            "GCP": partial(
                process_instances, _connect, "RUNNING", (instance_name,), **kwargs
            ),
            "AZURE": partial(
                process_instances, _connect, "VM running", (instance_name,), **kwargs
            ),
        }[default_platform.upper()]()
    _unsupported_platform(default_platform)
