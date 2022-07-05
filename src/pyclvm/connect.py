# -*- coding: utf-8 -*- #

from functools import partial
from typing import Dict, Union

from instance._process import process_instances

from pyclvm._common.gcp_instance_mapping import GcpRemoteShellProxy
from pyclvm.plt import _default_platform, _unsupported_platform
from pyclvm.ssm.session import start as start_session


# ---
def _connect_gcp(instance_name: str, instance: GcpRemoteShellProxy, **kwargs) -> None:
    print(f"Connecting to {instance_name} ...")
    instance.execute((), **kwargs)  # TODO change Instance type to GcpRemoteShellProxy


def connect(instance_name: str, **kwargs: str) -> Union[Dict, None]:
    """
    connect to a virtual machine

    Args:
        instance_name (str): virtual machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None

    """
    supported_platforms = {"AWS", "GCP", "AZURE"}

    platform = _default_platform(**kwargs)

    if platform in supported_platforms:
        return {
            "AWS": partial(start_session, instance_name, **kwargs),
            "GCP": partial(
                process_instances, _connect_gcp, "RUNNING", (instance_name,), kwargs
            ),
            "AZURE": ...,
        }[platform.upper()]()
    else:
        _unsupported_platform(platform)
