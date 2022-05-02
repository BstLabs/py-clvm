from functools import partial
from typing import Any, Callable, Optional, Tuple

from boto3.session import Session

from ._mapping import Instance
from ._process import process_instances


def _start_instance(
    instance_name: str, instance: Instance
) -> Optional[Callable[..., Any]]:
    _state = instance.state.Name
    _state_map = {
        "running": partial(_is_running, instance_name),
        "stopped": partial(_is_stopped_or_terminated, instance_name, instance),
        "terminated": partial(_is_stopped_or_terminated, instance_name, instance),
    }
    return _state_map[_state]


def _is_running(instance_name: str) -> str:
    print(f"{instance_name} is running.")
    return "running"


def _is_stopped_or_terminated(instance_name: str, instance: Instance) -> str:
    print(f"Starting {instance_name} ...")
    instance.start()
    instance.wait_until_running()
    print(f"{instance_name} is running")
    return "starting"


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
