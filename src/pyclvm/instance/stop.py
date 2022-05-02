from functools import partial
from typing import Any, Callable, Optional

from ._mapping import Instance
from ._process import process_instances


def _stop_instance(
    instance_name: str, instance: Instance
) -> Optional[Callable[..., Any]]:
    _state = instance.state.Name
    _state_map = {
        "stopped": partial(_is_already_stopped, instance_name),
        "terminated": partial(_is_terminated, instance_name),
        "running": partial(_is_stopping, instance_name, instance),
    }
    return _state_map[_state]


def _is_already_stopped(instance_name: str) -> str:
    print(f"{instance_name} is already stopped.")
    return "stopped"


def _is_terminated(instance_name: str) -> str:
    print(f"{instance_name} is terminated.")
    return "terminated"


def _is_stopping(instance_name: str, instance: Instance) -> str:
    print(f"Stopping {instance_name} ...")
    instance.stop()
    instance.wait_until_stopped()
    print(f"{instance_name} stopped.")
    return "in transition"


def stop(*instance_names: str, **kwargs: str) -> None:
    """
    stop vm instance

    Args:
        *instance_names (str): list of instance names, if empty will stop all running instances
        **kwargs (str): (optional) additional arguments, currently only profile

    Returns:
        None
    """
    process_instances(_stop_instance, "running", instance_names, kwargs)
