from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, Optional, Tuple

from ec2instances.ec2_instance_mapping import Ec2RemoteShellMapping

from pyclvm._common.session import Session, get_session
from pyclvm._common.gcp_instance_mapping import GcpRemoteShellMapping

def _process_many(
    func: Callable, state: str, instance_names: Tuple[str], kwargs: Dict[str, str]
) -> None:

    instances = list(
        (name, instance)
        for name, instance in Ec2RemoteShellMapping(get_session(kwargs)).items()
        if instance.name in instance_names
    )
    with ThreadPoolExecutor() as executor:
        res = executor.map(lambda t: func(*t), instances)
        print(list(res))
    return None


def _process_one(
    func: Callable, instance_name: str, kwargs: Dict[str, str]
) -> Tuple[Session, str]:
    # TODO move the getting platform out of here
    platform = kwargs.get("platform", "aws")
    if platform == "aws":
        instances = Ec2RemoteShellMapping(get_session(kwargs))
    elif platform == "gcp":
        instances = GcpRemoteShellMapping()
    elif platform == "gcp":
        pass
    else:
        raise RuntimeError("Unsupported platform")

    instance = instances.get(instance_name)
    if not instance:
        raise RuntimeError(
            "[ERROR] No such instance registered: wrong instance name provided"
        )
    func(instance_name, instance)
    return instance.session, instance.id


def process_instances(
    func: Callable, state: str, instance_names: Tuple[str], kwargs: Dict[str, str]
) -> Optional[Tuple[Session, str]]:
    return (
        _process_one(func, instance_names[0], kwargs)
        if len(instance_names) == 1
        else _process_many(func, state, instance_names, kwargs)
    )
