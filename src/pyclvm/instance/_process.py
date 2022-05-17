from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, Optional, Tuple

from ec2instances.common.session import Session
from ec2instances.ec2_instance_mapping import Ec2RemoteShellMapping


def _process_many(
    func: Callable, state: str, instance_names: Tuple[str], kwargs: Dict[str, str]
) -> None:

    instances = list(
        (name, instance)
        for name, instance in Ec2RemoteShellMapping(**kwargs).items()
        if instance.name in instance_names
    )
    with ThreadPoolExecutor() as executor:
        res = executor.map(lambda t: func(*t), instances)
        print(list(res))
    return None


def _process_one(
    func: Callable, instance_name: str, kwargs: Dict[str, str]
) -> Tuple[Session, str]:
    instances = Ec2RemoteShellMapping(**kwargs)
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
