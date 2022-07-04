"""start vm instance"""

from functools import partial
from typing import Any, Dict, Union

from ec2instances.ec2_instance_mapping import Ec2InstanceProxy

from pyclvm._common.gcp_instance_mapping import GcpInstanceProxy
from pyclvm.plt import _create_cache, _default_platform, _unsupported_platform

from ._process import process_instances


def _start_instance(
    instance_name: str, instance: Union[Ec2InstanceProxy, GcpInstanceProxy], **kwargs
) -> Any:
    platform = _default_platform(**kwargs)
    return {
        "AWS": partial(_start_instance_aws, instance_name, instance, **kwargs),
        "GCP": partial(_start_instance_gcp, instance_name, instance, **kwargs),
        "AZURE": partial(_start_instance_azure, **kwargs),
    }[platform.upper()]()


def _start_instance_aws(
    instance_name: str, instance: Ec2InstanceProxy, **kwargs
) -> Any:
    return {
        "running": partial(_is_running, instance_name),
        "stopped": partial(_is_stopped_or_terminated, instance_name, instance),
        "terminated": partial(_is_stopped_or_terminated, instance_name, instance),
        "stopping": partial(_in_transition, instance_name, instance),
        "pending": partial(_in_transition, instance_name, instance),
        "shutting-down": partial(_in_transition, instance_name, instance),
        "rebooting": partial(_in_transition, instance_name, instance),
    }[instance.state.name]()


def _start_instance_gcp(
    instance_name: str, instance: GcpInstanceProxy, **kwargs
) -> Any:
    return {
        "RUNNING": partial(_is_running, instance_name),
        "STOPPED": partial(_is_stopped_or_terminated, instance_name, instance),
        "TERMINATED": partial(_is_stopped_or_terminated, instance_name, instance),
        "SUSPENDED": partial(_is_stopped_or_terminated, instance_name, instance),
        "STOPPING": partial(_in_transition, instance_name, instance),
        "PROVISIONING": partial(_in_transition, instance_name, instance),
        "DEPROVISIONING": partial(_in_transition, instance_name, instance),
        "REPAIRING": partial(_in_transition, instance_name, instance),
        "STAGING": partial(_in_transition, instance_name, instance),
        "SUSPENDING": partial(_in_transition, instance_name, instance),
    }[instance.state]()


def _start_instance_azure():
    ...


def _is_running(instance_name: str) -> None:
    print(f"{instance_name} is running.")


def _is_stopped_or_terminated(
    instance_name: str, instance: Union[Ec2InstanceProxy, GcpInstanceProxy]
) -> None:
    print(f"Starting {instance_name} ...")
    instance.start()
    print(f"{instance_name} is running")


def _in_transition(
    instance_name: str, instance: Union[Ec2InstanceProxy, GcpInstanceProxy]
) -> None:
    print(
        f"{instance_name} is now in transition state. Wait untill current state is determined."
    )
    # TODO TODO handle transition mode
    # instance.wait_until_exists()
    print(f"{instance_name} is {instance.state.name}")


def start(*instance_names: str, **kwargs) -> Union[Dict, None]:
    """
    start vm instance

    Args:
        *instance_names (str): list of instance names (if empty will start all stopped instances)
        **kwargs (str): (optional) additional arguments, currently only profile

    Returns:
        Tuple[Session, instance_is (str)]
    """
    supported_platforms = {"AWS", "GCP", "AZURE"}
    try:
        platform = _default_platform(**kwargs)

        if platform in supported_platforms:
            return {
                "AWS": partial(_start_aws, *instance_names, **kwargs),
                "GCP": partial(_start_gcp, *instance_names, **kwargs),
                "AZURE": partial(_start_azure, *instance_names, **kwargs),
            }
        else:
            _unsupported_platform(platform)
    except FileNotFoundError:
        _create_cache()


# ---
def _start_aws(*instance_names: str, **kwargs):
    return process_instances(_start_instance, "stopped", instance_names, kwargs)


# ---
def _start_gcp(*instance_names: str, **kwargs):
    return process_instances(_start_instance, "TERMINATED", instance_names, kwargs)


# ---
def _start_azure(*instance_names: str, **kwargs):
    ...
