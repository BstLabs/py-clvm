from functools import partial
from typing import Any, Optional, Tuple, Union

from boto3.session import Session

from ._mapping import Instance
from ._process import process_instances
from pyclvm._common.gcp_instance_mapping import GcpInstanceProxy
from ec2instances.ec2_instance_mapping import Ec2InstanceProxy

# TODO move the getting platform out of here
platform = None


def _start_instance(instance_name: str, instance: Union[Ec2InstanceProxy, GcpInstanceProxy], **kwargs) -> Any:
    if platform == "aws":
        return {
            "running": partial(_is_running, instance_name),
            "stopped": partial(_is_stopped_or_terminated, instance_name, instance),
            "terminated": partial(_is_stopped_or_terminated, instance_name, instance),
            "stopping": partial(_in_transition, instance_name, instance),
            "pending": partial(_in_transition, instance_name, instance),
            "shutting-down": partial(_in_transition, instance_name, instance),
            "rebooting": partial(_in_transition, instance_name, instance),
        }[instance.state.name]()
    elif platform == "gcp":
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
    elif platform == "azure":
        pass
    else:
        raise RuntimeError("Unsupported platform")


def _is_running(instance_name: str) -> None:
    print(f"{instance_name} is running.")


def _is_stopped_or_terminated(instance_name: str, instance: Union[Ec2InstanceProxy, GcpInstanceProxy]) -> None:
    print(f"Starting {instance_name} ...")
    instance.start()
    print(f"{instance_name} is running")


def _in_transition(instance_name: str, instance: Union[Ec2InstanceProxy, GcpInstanceProxy]) -> None:
    print(
        f"{instance_name} is now in transition state. Wait untill current state is determined."
    )
    # TODO TODO handle transition mode
    # instance.wait_until_exists()
    print(f"{instance_name} is {instance.state.name}")


def start(*instance_names: str, **kwargs: str) -> Optional[Tuple[Session, str]]:
    """
    start vm instance

    Args:
        *instance_names (str): list of instance names (if empty will start all stopped instances)
        **kwargs (str): (optional) additional arguments, currently only profile

    Returns:
        Tuple[Session, instance_is (str)]
    """
    global platform
    platform = kwargs.get("platform", "aws")

    if platform == "aws":
        return _start_aws(*instance_names, **kwargs)
    elif platform == "gcp":
        return _start_gcp(*instance_names, **kwargs)
    elif platform == "azure":
        return _start_azure(*instance_names, **kwargs)
    else:
        raise RuntimeError("Unsupported platform")


# ---
def _start_aws(*instance_names: str, **kwargs: str):
    return process_instances(_start_instance, "stopped", instance_names, kwargs)


# ---
def _start_gcp(*instance_names: str, **kwargs: str):
    return process_instances(_start_instance, "TERMINATED", instance_names, kwargs)


# ---
def _start_azure(*instance_names: str, **kwargs: str):
    pass
