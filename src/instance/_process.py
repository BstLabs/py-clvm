from collections import ChainMap
from _common.session import Session
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, Dict, Optional, Callable
from ._mapping import InstanceMapping, Instance


def _process_many(
    func: Callable, 
    state: str, 
    instance_names: Tuple[str], 
    kwargs: Dict[str, str]
) -> None:
    instances = InstanceMapping(**ChainMap(
        kwargs,
        dict(names=instance_names) if instance_names else dict(states=state)
    ))

    items = list(instances.items())
    with ThreadPoolExecutor() as pool:
        pool.map(lambda t: func(*t), items, chunksize=10)
    return None


def _process_one(func: Callable, instance_name: str, kwargs: Dict[str, str]) -> Tuple[Session, str]:
    instances = InstanceMapping(**kwargs)
    instance = instances[instance_name]
    func(instance_name, instance)
    return instances.session, instance.instance_id


def process_instances(
    func: Callable,
    state: str,
    instance_names: Tuple[str], 
    kwargs: Dict[str, str]
) -> Optional[Tuple[Session, str]]:
    return _process_one(func, next(instance_names), kwargs) \
           if 1 == len(instance_names) else \
           _process_many(func, state, instance_names, kwargs)

