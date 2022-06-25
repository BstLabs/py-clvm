from ._mapping import Instance
from ._process import process_instances


def _execute(instance_name: str, instance: Instance, **kwargs) -> None:
    print(f"Working {instance_name} ...")
    instance.execute(kwargs.get("script"))


def command(instance_name: str, script: str, **kwargs: str) -> None:
    """
    not implemented
    """
    kwargs["script"] = script
    process_instances(_execute, "running", (instance_name, ), kwargs)
