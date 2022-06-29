from functools import partial
from typing import Union, Any

from ._mapping import Instance
from ._process import process_instances

from pyclvm._common.gcp_instance_mapping import GcpInstanceProxy
from pyclvm._common.azure_instance_mapping import AzureInstanceProxy
from ec2instances.ec2_instance_mapping import Ec2InstanceProxy


# TODO move the getting platform out of here
platform = None


def _stop_instance(instance_name: str, instance: Union[Ec2InstanceProxy, GcpInstanceProxy, AzureInstanceProxy], **kwargs) -> Any:
    if platform == "aws":
        return {
            "stopped": partial(_is_already_stopped, instance_name),
            "terminated": partial(_is_terminated, instance_name),
            "running": partial(_stopping_instance, instance_name, instance),
            "stopping": partial(_in_transition, instance_name, instance),
            "pending": partial(_in_transition, instance_name, instance),
            "shutting-down": partial(_in_transition, instance_name, instance),
            "rebooting": partial(_in_transition, instance_name, instance),
        }[instance.state.name]()
    elif platform == "gcp":
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
    elif platform == "azure":
        return {
            "VM stopped": partial(_is_already_stopped, instance_name),
            "VM deallocated": partial(_is_terminated, instance_name),
            "VM running": partial(_stopping_instance, instance_name, instance),
            "VM stopping": partial(_in_transition, instance_name, instance),
            "VM starting": partial(_in_transition, instance_name, instance),
            "VM deallocating": partial(_in_transition, instance_name, instance),
            "Provisioning succeeded": partial(_in_transition, instance_name, instance),
        }[instance.state]()

    else:
        raise RuntimeError("Unsupported platform")


def _is_already_stopped(instance_name: str) -> None:
    print(f"{instance_name} is already stopped.")


def _is_terminated(instance_name: str) -> None:
    print(f"{instance_name} is terminated.")


def _stopping_instance(instance_name: str, instance: Union[Ec2InstanceProxy, GcpInstanceProxy, AzureInstanceProxy]) -> None:
    print(f"Stopping {instance_name} ...")
    instance.stop()
    print(f"{instance_name} stopped.")


def _in_transition(instance_name: str, instance: Union[Ec2InstanceProxy, GcpInstanceProxy, AzureInstanceProxy]) -> None:
    print(
        f"{instance_name} is now in transition state. Wait until current state is determined."
    )
    # TODO handle transition mode
    # instance.wait_until_exists()
    _state = instance.state if isinstance(instance.state, str) else instance.state.name
    print(f"{instance_name} is {_state}")


def stop(*instance_names: str, **kwargs: str) -> None:
    """
    stop vm instance

    Args:
        *instance_names (str): list of instance names, if empty will stop all running instances
        **kwargs (str): (optional) additional arguments, currently only profile

    Returns:
        None
    """
    global platform
    platform = kwargs.get("platform", "aws")

    if platform == "aws":
        _stop_aws(*instance_names, **kwargs)
    elif platform == "gcp":
        _stop_gcp(*instance_names, **kwargs)
    elif platform == "azure":
        _stop_azure(*instance_names, **kwargs)
    else:
        raise RuntimeError("Unsupported platform")


# ---
def _stop_aws(*instance_names: str, **kwargs: str):
    process_instances(_stop_instance, "running", instance_names, kwargs)


# ---
def _stop_gcp(*instance_names: str, **kwargs: str):
    process_instances(_stop_instance, "RUNNING", instance_names, kwargs)


# ---
def _stop_azure(*instance_names: str, **kwargs: str):
    process_instances(_stop_instance, "VM running", instance_names, kwargs)

