"""stop vm instance"""

from functools import partial
from typing import Any, Dict, Union

from ec2instances.ec2_instance_mapping import Ec2InstanceProxy

from pyclvm._common.azure_instance_mapping import AzureInstanceProxy
from pyclvm._common.gcp_instance_mapping import GcpInstanceProxy
from pyclvm.plt import (
    _default_platform,
    _get_supported_platforms,
    _unsupported_platform,
)

from ._process import process_instances


def _stop_instance_aws(
    instance_name: str, instance: Ec2InstanceProxy, **kwargs: str
) -> Any:

    return {
        "stopped": partial(_is_already_stopped, instance_name),
        "terminated": partial(_is_terminated, instance_name),
        "running": partial(_stopping_instance, instance_name, instance),
        "stopping": partial(_in_transition, instance_name, instance),
        "pending": partial(_in_transition, instance_name, instance),
        "shutting-down": partial(_in_transition, instance_name, instance),
        "rebooting": partial(_in_transition, instance_name, instance),
    }[instance.state.name]()


def _stop_instance_gcp(
    instance_name: str, instance: GcpInstanceProxy, **kwargs: str
) -> Any:
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


def _stop_instance_azure(
    instance_name: str, instance: AzureInstanceProxy, **kwargs: str
) -> Any:
    return {
        "VM stopped": partial(_is_already_stopped, instance_name),
        "VM deallocated": partial(_is_terminated, instance_name),
        "VM running": partial(_stopping_instance, instance_name, instance),
        "VM stopping": partial(_in_transition, instance_name, instance),
        "VM starting": partial(_in_transition, instance_name, instance),
        "VM deallocating": partial(_in_transition, instance_name, instance),
        "Provisioning succeeded": partial(_in_transition, instance_name, instance),
    }[
        instance.state
    ]()  # type: ignore


def _is_already_stopped(instance_name: str) -> None:
    print(f"{instance_name} is already stopped.")


def _is_terminated(instance_name: str) -> None:
    print(f"{instance_name} is terminated.")


def _stopping_instance(
    instance_name: str,
    instance: Union[Ec2InstanceProxy, GcpInstanceProxy, AzureInstanceProxy],
) -> None:
    print(f"Stopping {instance_name} ...")
    print(instance.stop(wait=False))


def _in_transition(
    instance_name: str,
    instance: Union[Ec2InstanceProxy, GcpInstanceProxy, AzureInstanceProxy],
) -> None:
    print(
        f"{instance_name} is now in transition state. Wait untill current state is determined."
    )
    # TODO handle transition mode
    # instance.wait_until_exists()
    _state = instance.state if isinstance(instance.state, str) else instance.state.name
    print(f"{instance_name} is {_state}")


def stop(*instance_names: str, **kwargs: str) -> Union[Dict, None]:
    """
    stop vm instance

    Args:
        *instance_names (str): list of instance names, if empty will stop all running instances
        **kwargs (str): (optional) additional arguments, currently only profile

    Returns:
        None
    """
    default_platform, supported_platforms = (
        _default_platform(**kwargs),
        _get_supported_platforms(),
    )

    if default_platform in supported_platforms:
        return {
            "AWS": partial(_stop_aws, *instance_names, **kwargs),
            "GCP": partial(_stop_gcp, *instance_names, **kwargs),
            "AZURE": partial(_stop_azure, *instance_names, **kwargs),
        }[default_platform.upper()]()
    else:
        _unsupported_platform(default_platform)


# ---
def _stop_aws(*instance_names: str, **kwargs: str):
    process_instances(_stop_instance_aws, "running", instance_names, **kwargs)


# ---
def _stop_gcp(*instance_names: str, **kwargs: str):
    process_instances(_stop_instance_gcp, "RUNNING", instance_names, **kwargs)


# ---
def _stop_azure(*instance_names: str, **kwargs: str):
    process_instances(_stop_instance_azure, "VM running", instance_names, **kwargs)
