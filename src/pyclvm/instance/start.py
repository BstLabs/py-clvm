from functools import partial
from typing import Any, Optional, Tuple

from boto3.session import Session

from ._mapping import Instance
from ._process import process_instances


def _start_instance(instance_name: str, instance: Instance) -> Any:
    return {
        "running": partial(_is_running, instance_name),
        "stopped": partial(_is_stopped_or_terminated, instance_name, instance),
        "terminated": partial(_is_stopped_or_terminated, instance_name, instance),
        "stopping": partial(_in_transition, instance_name, instance),
        "pending": partial(_in_transition, instance_name, instance),
        "shutting-down": partial(_in_transition, instance_name, instance),
        "rebooting": partial(_in_transition, instance_name, instance),
    }[instance.state.Name]()


def _is_running(instance_name: str) -> None:
    print(f"{instance_name} is running.")


def _is_stopped_or_terminated(instance_name: str, instance: Instance) -> None:
    print(f"Starting {instance_name} ...")
    instance.start()
    instance.wait_until_running()
    print(f"{instance_name} is running")


def _in_transition(instance_name: str, instance: Instance) -> None:
    print(
        f"{instance_name} is now in transition state. Wait untill current state is determined."
    )
    instance.wait_until_exists()
    print(f"{instance_name} is {instance.state.Name}")


def start(*instance_names: str, **kwargs: str) -> Optional[Tuple[Session, str]]:
    """
    start vm instance

    Args:
        *instance_names (str): list of instance names (if empty will start all stopped instances)
        **kwargs (str): (optional) additional arguments, currently only profile

    Returns:
        Tuple[Session, instance_is (str)]
    """
    return process_instances(_start_instance, "stopped", instance_names, kwargs)
