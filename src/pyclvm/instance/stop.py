from functools import partial
from typing import Any

from ._mapping import Instance
from ._process import process_instances


def _stop_instance(instance_name: str, instance: Instance) -> Any:
    return {
        "stopped": partial(_is_already_stopped, instance_name),
        "terminated": partial(_is_terminated, instance_name),
        "running": partial(_stopping_instance, instance_name, instance),
        "stopping": partial(_in_transition, instance_name, instance),
        "pending": partial(_in_transition, instance_name, instance),
        "shutting-down": partial(_in_transition, instance_name, instance),
        "rebooting": partial(_in_transition, instance_name, instance),
    }[instance.state.Name]()


def _is_already_stopped(instance_name: str) -> None:
    print(f"{instance_name} is already stopped.")


def _is_terminated(instance_name: str) -> None:
    print(f"{instance_name} is terminated.")


def _stopping_instance(instance_name: str, instance: Instance) -> None:
    print(f"Stopping {instance_name} ...")
    instance.stop()
    instance.wait_until_stopped()
    print(f"{instance_name} stopped.")


def _in_transition(instance_name: str, instance: Instance) -> None:
    print(
        f"{instance_name} is now in transition state. Wait untill current state is determined."
    )
    instance.wait_until_exists()
    print(f"{instance_name} is {instance.state.Name}")


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
