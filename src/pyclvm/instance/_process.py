from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Callable, Dict, Optional, Tuple, Union

from ec2instances.ec2_instance_mapping import Ec2RemoteShellMapping

from pyclvm._common.azure_instance_mapping import AzureRemoteShellMapping
from pyclvm._common.gcp_instance_mapping import GcpRemoteShellMapping
from pyclvm._common.session import Session, get_session
from pyclvm.plt import _default_platform, _unsupported_platform


def _process_aws(**kwargs: str) -> Ec2RemoteShellMapping:
    return Ec2RemoteShellMapping(get_session(kwargs))


def _process_gcp(**kwargs: str) -> GcpRemoteShellMapping:
    return GcpRemoteShellMapping()


def _process_azure(**kwargs: str):
    return AzureRemoteShellMapping()


def _return_instances(**kwargs) -> Union[Dict, None]:
    platform, supported_platforms = _default_platform(**kwargs)
    if platform in supported_platforms:
        return {
            "AWS": partial(_process_aws, **kwargs),
            "GCP": partial(_process_gcp, **kwargs),
            "AZURE": partial(_process_azure, **kwargs),
        }[platform.upper()]()
    else:
        _unsupported_platform(platform)
        return None


def _process_many(
    func: Callable, state: str, instance_names: Tuple[str], kwargs: Dict[str, str]
) -> None:
    # TODO realize platform selection
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

    instance = _return_instances(**kwargs).get(instance_name)

    if not instance:
        raise RuntimeError(
            "[ERROR] No such instance registered: wrong instance name provided"
        )
    func(instance_name, instance, **kwargs)
    return instance.session, instance.id


def process_instances(
    func: Callable, state: str, instance_names: Tuple[str], kwargs: Dict[str, str]
) -> Optional[Tuple[Session, str]]:
    return (
        _process_one(func, instance_names[0], kwargs)
        if len(instance_names) == 1
        else _process_many(func, state, instance_names, kwargs)
    )
