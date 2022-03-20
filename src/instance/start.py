from ._mapping import Instance
from typing import Tuple, Optional
from _common.session import Session
from ._process import process_instances


def _start_instance(instance_name: str, instance: Instance) -> None:
    if 'stopped' == instance.state.Name:
        print(f'Starting {instance_name} ...')
        instance.start()
        instance.wait_until_running()
    print(f'{instance_name} is running')


def start(*instance_names: str, **kwargs: str) -> Optional[Tuple[Session, str]]:
    """
    start vm instance

    Args:
        *instance_names (str): list of instance names (if empty will start all stopped instances)
        **kwargs (str): (optional) additional arguments, currently only profile

    Returns:
        Tuple[Session, instance_is (str)]
    """
    process_instances(_start_instance, 'stopped', instance_names, kwargs)

