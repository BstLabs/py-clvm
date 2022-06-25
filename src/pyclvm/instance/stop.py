from functools import partial
from typing import Any

from ._mapping import Instance
from ._process import process_instances

# TODO move the getting platform out of here
platform = None


def _stop_instance(instance_name: str, instance: Instance) -> Any:
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
        pass
    else:
        raise RuntimeError("Unsupported platform")


def _is_already_stopped(instance_name: str) -> None:
    print(f"{instance_name} is already stopped.")


def _is_terminated(instance_name: str) -> None:
    print(f"{instance_name} is terminated.")


def _stopping_instance(instance_name: str, instance: Instance) -> None:
    print(f"Stopping {instance_name} ...")
    instance.stop()
    print(f"{instance_name} stopped.")


def _in_transition(instance_name: str, instance: Instance) -> None:
    print(
        f"{instance_name} is now in transition state. Wait untill current state is determined."
    )
    instance.wait_until_exists()
    print(f"{instance_name} is {instance.state.name}")


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
    process_instances(_stop_instance, "TERMINATED", instance_names, kwargs)


# ---
def _stop_azure(*instance_names: str, **kwargs: str):
    pass
