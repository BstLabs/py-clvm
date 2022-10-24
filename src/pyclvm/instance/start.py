"""start vm instance"""

from functools import partial
from typing import Any, Tuple, Union

from ec2instances.ec2_instance_mapping import Ec2InstanceProxy

from pyclvm._common.azure_instance_mapping import AzureInstanceProxy
from pyclvm._common.gcp_instance_mapping import GcpInstanceProxy
from pyclvm.plt import (
    _default_platform,
    _get_supported_platforms,
    _unsupported_platform,
)

from ._process import process_instances


def _start_instance_aws(
    instance_name: str, instance: Ec2InstanceProxy, **kwargs: str
) -> Any:
    return {
        "running": partial(_is_running, instance_name, **kwargs),
        "stopped": partial(
            _is_stopped_or_terminated, instance_name, instance, **kwargs
        ),
        "terminated": partial(
            _is_stopped_or_terminated, instance_name, instance, **kwargs
        ),
        "stopping": partial(_in_transition, instance_name, instance, **kwargs),
        "pending": partial(_in_transition, instance_name, instance, **kwargs),
        "shutting-down": partial(_in_transition, instance_name, instance, **kwargs),
        "rebooting": partial(_in_transition, instance_name, instance, **kwargs),
    }[instance.state.name]()


def _start_instance_gcp(
    instance_name: str, instance: GcpInstanceProxy, **kwargs: str
) -> Any:
    return {
        "RUNNING": partial(_is_running, instance_name, **kwargs),
        "STOPPED": partial(
            _is_stopped_or_terminated, instance_name, instance, **kwargs
        ),
        "TERMINATED": partial(
            _is_stopped_or_terminated, instance_name, instance, **kwargs
        ),
        "SUSPENDED": partial(
            _is_stopped_or_terminated, instance_name, instance, **kwargs
        ),
        "STOPPING": partial(_in_transition, instance_name, instance, **kwargs),
        "PROVISIONING": partial(_in_transition, instance_name, instance, **kwargs),
        "DEPROVISIONING": partial(_in_transition, instance_name, instance, **kwargs),
        "REPAIRING": partial(_in_transition, instance_name, instance, **kwargs),
        "STAGING": partial(_in_transition, instance_name, instance, **kwargs),
        "SUSPENDING": partial(_in_transition, instance_name, instance, **kwargs),
    }[instance.state]()


def _start_instance_azure(
    instance_name: str, instance: AzureInstanceProxy, **kwargs: str
) -> Any:
    return {
        "VM running": partial(_is_running, instance_name, **kwargs),
        "VM stopped": partial(
            _is_stopped_or_terminated, instance_name, instance, **kwargs
        ),
        "VM deallocated": partial(
            _is_stopped_or_terminated, instance_name, instance, **kwargs
        ),
        "VM stopping": partial(_in_transition, instance_name, instance, **kwargs),
        "VM starting": partial(_in_transition, instance_name, instance, **kwargs),
        "VM deallocating": partial(_in_transition, instance_name, instance, **kwargs),
        "Provisioning succeeded": partial(
            _in_transition, instance_name, instance, **kwargs
        ),
    }[
        instance.state
    ]()  # type: ignore


def _is_running(instance_name: str, **kwargs) -> None:
    print(f"{instance_name} is running.")


def _is_stopped_or_terminated(
    instance_name: str,
    instance: Union[Ec2InstanceProxy, GcpInstanceProxy, AzureInstanceProxy],
    wait: bool = False,
    **kwargs: str,
) -> None:
    print(f"Starting {instance_name} ...")
    print(instance.start(wait=wait))


def _in_transition(
    instance_name: str,
    instance: Union[Ec2InstanceProxy, GcpInstanceProxy, AzureInstanceProxy],
    **kwargs,
) -> None:
    print(
        f"{instance_name} is now in transition state. Wait untill current state is determined."
    )
    # TODO TODO handle transition mode
    # instance.wait_until_exists()
    _state = instance.state if isinstance(instance.state, str) else instance.state.name
    print(f"{instance_name} is {_state}")


def start(*instance_names: str, **kwargs: str) -> Union[Tuple, None]:
    """
    start vm instance

    Args:
        *instance_names (str): list of instance names (if empty will start all stopped instances)
        **kwargs (str): (optional) additional arguments, currently only profile

    Returns:
        Union[Tuple, None]
    """
    default_platform, supported_platforms = (
        _default_platform(**kwargs),
        _get_supported_platforms(),
    )

    if default_platform in supported_platforms:
        return {
            "AWS": partial(_start_aws, *instance_names, **kwargs),
            "GCP": partial(_start_gcp, *instance_names, **kwargs),
            "AZURE": partial(_start_azure, *instance_names, **kwargs),
        }[default_platform.upper()]()
    _unsupported_platform(default_platform)


def _start_aws(*instance_names: str, **kwargs: str) -> Union[Tuple, None]:
    return process_instances(_start_instance_aws, "stopped", instance_names, **kwargs)


def _start_gcp(*instance_names: str, **kwargs: str) -> Union[Tuple, None]:
    return process_instances(
        _start_instance_gcp, "TERMINATED", instance_names, **kwargs
    )


def _start_azure(*instance_names: str, **kwargs: str) -> Union[Tuple, None]:
    return process_instances(
        _start_instance_azure, "VM deallocated", instance_names, **kwargs
    )
