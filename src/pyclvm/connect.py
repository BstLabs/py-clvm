from pyclvm.ssm.session import start as start_session
from instance._mapping import Instance
from instance._process import process_instances


# TODO move the getting platform out of here
platform = None


# ---
def _connect_gcp(instance_name: str, instance: Instance, **kwargs) -> None:
    print(f"Connecting to {instance_name} ...")
    instance.execute((), **kwargs)


def connect(instance_name: str, **kwargs: str) -> None:
    """
    connect to a virtual machine

    Args:
        instance_name (str): virtual machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None

    """
    global platform
    platform = kwargs.get("platform", "aws")

    if platform == "aws":
        start_session(instance_name, **kwargs)
    elif platform == "gcp":
        process_instances(_connect_gcp, "RUNNING", (instance_name, ), kwargs)
    elif platform == "azure":
        pass
    else:
        raise RuntimeError("Unsupported platform")


