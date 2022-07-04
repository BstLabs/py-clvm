"""stop vm instance"""

from functools import partial
from typing import Any, Dict, Union

from ec2instances.ec2_instance_mapping import Ec2InstanceProxy

from pyclvm._common.gcp_instance_mapping import GcpInstanceProxy
from pyclvm.plt import _create_cache, _default_platform, _unsupported_platform

from ._process import process_instances


def _stop_instance(
    instance_name: str, instance: Union[Ec2InstanceProxy, GcpInstanceProxy], **kwargs
) -> Any:
    platform = _default_platform(**kwargs)
    return {
        "AWS": partial(_stop_instance_aws, instance_name, instance, **kwargs),
        "GCP": partial(_stop_instance_gcp, instance_name, instance, **kwargs),
        "AZURE": partial(_stop_instance_azure, **kwargs),
    }[platform.upper()]()


def _stop_instance_aws(instance_name: str, instance: Ec2InstanceProxy, **kwargs) -> Any:

    return {
        "stopped": partial(_is_already_stopped, instance_name),
        "terminated": partial(_is_terminated, instance_name),
        "running": partial(_stopping_instance, instance_name, instance),
        "stopping": partial(_in_transition, instance_name, instance),
        "pending": partial(_in_transition, instance_name, instance),
        "shutting-down": partial(_in_transition, instance_name, instance),
        "rebooting": partial(_in_transition, instance_name, instance),
    }[instance.state.name]()


def _stop_instance_gcp(instance_name: str, instance: GcpInstanceProxy, **kwargs) -> Any:
    return {
        "STOPPED": partial(_is_already_stopped, instance_name),
        "SUSPENDED": partial(_is_already_stopped, instance_name),
        "TERMINATED": partial(_is_terminated, instance_name),
        "RUNNING": partial(_stopping_instance, instance_name, instance),
        "STOPPING": partial(_in_transition, instance_name, instance),
        "PROVISIONING": partial(_in_transition, instance_name, instance),
        "DEPROVISIONING": partial(_in_transition, instance_name, instance),
        "REPAIRING": partial(_in_transition, instance_name, instance),
        "STAGING": partial(_in_transition, instance_name, instance),
        "SUSPENDING": partial(_in_transition, instance_name, instance),
    }[instance.state]()


def _stop_instance_azure():
    ...


def _is_already_stopped(instance_name: str) -> None:
    print(f"{instance_name} is already stopped.")


def _is_terminated(instance_name: str) -> None:
    print(f"{instance_name} is terminated.")


def _stopping_instance(
    instance_name: str, instance: Union[Ec2InstanceProxy, GcpInstanceProxy]
) -> None:
    print(f"Stopping {instance_name} ...")
    instance.stop()
    print(f"{instance_name} stopped.")


def _in_transition(
    instance_name: str, instance: Union[Ec2InstanceProxy, GcpInstanceProxy]
) -> None:
    print(
        f"{instance_name} is now in transition state. Wait untill current state is determined."
    )
    # TODO handle transition mode
    # instance.wait_until_exists()
    print(f"{instance_name} is {instance.state.name}")


def stop(*instance_names: str, **kwargs) -> Union[Dict, None]:
    """
    stop vm instance

    Args:
        *instance_names (str): list of instance names, if empty will stop all running instances
        **kwargs (str): (optional) additional arguments, currently only profile

    Returns:
        None
    """
    supported_platforms = {"AWS", "GCP", "AZURE"}
    try:
        platform = _default_platform(**kwargs)

        if platform in supported_platforms:
            return {
                "AWS": _stop_aws(*instance_names, **kwargs),
                "GCP": _stop_gcp(*instance_names, **kwargs),
                "AZURE": _stop_azure(*instance_names, **kwargs),
            }
        else:
            _unsupported_platform(platform)
    except FileNotFoundError:
        _create_cache()


# ---
def _stop_aws(*instance_names: str, **kwargs):
    process_instances(_stop_instance, "running", instance_names, kwargs)


# ---
def _stop_gcp(*instance_names: str, **kwargs):
    process_instances(_stop_instance, "TERMINATED", instance_names, kwargs)


# ---
def _stop_azure(*instance_names: str, **kwargs):
    pass
