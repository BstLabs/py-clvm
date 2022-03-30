from ._mapping import Instance
from ._process import process_instances


def _stop_instance(instance_name: str, instance: Instance) -> None:
    if instance.state.Name == "running":
        print(f"Stopping {instance_name} ...")
        instance.stop()
        instance.wait_until_stopped()
    print(f"{instance_name} stopped")


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
