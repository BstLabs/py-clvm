# -*- coding: utf-8 -*- #

# from ._mapping import Instance
from pyclvm._common.gcp_instance_mapping import GcpRemoteShellProxy
from ._process import process_instances

# TODO move the getting platform out of here
platform = None


def _execute_aws(instance_name: str, instance: GcpRemoteShellProxy, **kwargs) -> None:
    print(f"Working {instance_name} ...")
    instance.execute(kwargs.get("script"), **kwargs)


def _execute_gcp(instance_name: str, instance: GcpRemoteShellProxy, **kwargs) -> None:
    print(f"Working {instance_name} ...")
    instance.execute((kwargs.get("script"), ), **kwargs)


def command(instance_name: str, script: str, **kwargs: str) -> None:
    """
    not implemented
    """
    kwargs["script"] = script

    global platform
    platform = kwargs.get("platform", "aws")

    if platform == "aws":
        process_instances(_execute_aws, "running", (instance_name, ), kwargs)
    elif platform == "gcp":
        process_instances(_execute_gcp, "RUNNING", (instance_name, ), kwargs)
    elif platform == "azure":
        pass
    else:
        raise RuntimeError("Unsupported platform")
