# -*- coding: utf-8 -*- #

from typing import AnyStr, Dict, Generator, Iterable, Iterator, Tuple, Union

from instances_map_abc.vm_instance_mapping import VmInstanceMappingBase
from instances_map_abc.vm_instance_proxy import VmInstanceProxy

from .azure_instance_proxy import AzureInstanceProxy, AzureRemoteShellProxy
from .session_azure import AzureSession, get_session


class AzureComputeAllInstancesData:
    """
    Derives all the instance data for further use.
    """

    def __init__(self, **kwargs) -> None:
        self._session = get_session(**kwargs)  # TODO get session out of here
        self._instances_data = self._instances()

    # ---
    def get_session(self) -> AzureSession:
        return self._session

    # ---
    @property
    def session(self) -> AzureSession:
        return self._session

    # ---
    def _instances(self) -> Iterable:
        return self._session.instances

    # ---
    def __iter__(self) -> Iterator:
        yield from self._instances_data

    # ---
    @staticmethod
    def _get_instance_name(tags: Dict) -> Union[AnyStr, None]:
        """
        Returns VM name from a tag
        :params _tags: Azure compute VM tags object
        :return: (str) Name of VM
        """
        try:
            for _key, _value in tags.items():
                if _key.upper() == "NAME":
                    return _value
        except AttributeError:
            pass


# ---
class AzureInstanceMapping(VmInstanceMappingBase[VmInstanceProxy]):
    def __init__(self, **kwargs) -> None:
        self._session = get_session(**kwargs)  # TODO get session out of here
        self._kwargs = kwargs

    def __getitem__(self, instance_name: str) -> AzureInstanceProxy:
        return self._get_instance(instance_name=instance_name)

    def __iter__(self) -> Iterator:
        for instance_name, _ in self._session.instances.items():
            yield self._get_instance(instance_name)

    def __len__(self) -> int:
        return sum(1 for _ in self)

    def keys(self) -> Generator[str, None, None]:
        for instance in self:
            yield instance.name

    def values(self) -> Generator[str, None, None]:
        yield from self

    def items(self) -> Generator[Tuple[str, str], None, None]:
        yield from zip(self.keys(), self.values())

    def _get_instance(self, instance_name: str) -> AzureInstanceProxy:
        return AzureInstanceProxy(
            instance_name=instance_name,
            session=self._session,
            **self._kwargs,
        )

    @property
    def session(self):
        return self._session


# ---
class AzureRemoteShellMapping(AzureInstanceMapping, VmInstanceMappingBase):
    def _get_instance(self, instance_name: str) -> AzureRemoteShellProxy:
        return AzureRemoteShellProxy(instance_name, self._session, **self._kwargs)
