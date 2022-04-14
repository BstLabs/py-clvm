from collections import ChainMap
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, Optional, Tuple

from pyclvm._common.session import Session

from ._mapping import InstanceMapping


def _process_many(
    func: Callable, state: str, instance_names: Tuple[str], kwargs: Dict[str, str]
) -> None:
    instances = InstanceMapping(
        **ChainMap(
            kwargs, {"names": instance_names} if instance_names else {"states": state}
        ),
    )

    items = list(instances.items())
    with ThreadPoolExecutor() as pool:
        pool.map(lambda t: func(*t), items, chunksize=10)
    return None


def _process_one(
    func: Callable, instance_name: str, kwargs: Dict[str, str]
) -> Tuple[Session, str]:
    instances = InstanceMapping(**kwargs)
    instance = instances.get(instance_name)
    if not instance:
        raise RuntimeError(
            "[ERROR] No such instance registered: wrong instance name provided"
        )
    func(instance_name, instance)
    return instances.session, instance.instance_id


def process_instances(
    func: Callable, state: str, instance_names: Tuple[str], kwargs: Dict[str, str]
) -> Optional[Tuple[Session, str]]:
    return (
        _process_one(func, instance_names[0], kwargs)
        if len(instance_names) == 1
        else _process_many(func, state, instance_names, kwargs)
    )
