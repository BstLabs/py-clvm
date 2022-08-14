# -*- coding: utf-8 -*- #

from typing import AnyStr, Generator, Iterable, Iterator, Tuple, Union

from google.cloud import compute_v1
from instances_map_abc.vm_instance_mapping import VmInstanceMappingBase
from instances_map_abc.vm_instance_proxy import VmInstanceProxy

from .gcp_instance_proxy import GcpInstanceProxy, GcpRemoteShellProxy
from .session_gcp import GcpSession, get_session


class GcpComputeAllInstancesData:
    """
    Derives all the instance data for further use.
    """

    def __init__(self, **kwargs) -> None:
        self._session = get_session(**kwargs)  # TODO get session out of here
        self._client = self._session.get_client()
        self._zone = self._session.get_zone()
        self._instances_data = self._instances()

    # ---
    def get_session(self) -> GcpSession:
        return self._session

    # ---
    @property
    def session(self) -> GcpSession:
        return self._session

    # ---
    def _instances(self) -> Iterable:
        return [
            (
                _instance.id,
                self._get_instance_name(_instance.tags) or _instance.name,
                _instance.status,
            )
            for _instance in self._session.instances
        ]

    # ---
    def __iter__(self) -> Iterator:
        yield from self._instances_data

    # ---
    @staticmethod
    def _get_instance_name(_tags: compute_v1.types.compute.Tags) -> Union[AnyStr, None]:
        """
        Returns VM name from a tag
        :params _tags: GCP compute VM tags object
        :return: (str) Name of VM
        """
        try:
            return _tags.name
        except AttributeError:
            pass


# ---
class GcpInstanceMapping(VmInstanceMappingBase[VmInstanceProxy]):
    def __init__(self, **kwargs) -> None:
        self._session = get_session(**kwargs)  # TODO get session out of here
        self._client = self._session.get_client()
        self._kwargs = kwargs

    def __getitem__(self, instance_name: str) -> GcpInstanceProxy:
        return self._get_instance(instance_name=instance_name)

    def __iter__(self) -> Iterator:
        # instances = (
        #     r["Instances"][0] for r in self._client.describe_instances()["Reservations"]
        # )
        for instance in self._session.instances:
            yield self._get_instance(instance.name)

    def __len__(self) -> int:
        return sum(1 for _ in self)

    def keys(self) -> Generator[str, None, None]:
        for instance in self:
            yield instance.name

    def values(self) -> Generator[str, None, None]:
        yield from self

    def items(self) -> Generator[Tuple[str, str], None, None]:
        yield from zip(self.keys(), self.values())

    def _get_instance(self, instance_name: str) -> GcpInstanceProxy:
        return GcpInstanceProxy(
            instance_name=instance_name,
            session=self._session,
            **self._kwargs,
        )

    @property
    def session(self):
        return self._session


# ---
class GcpRemoteShellMapping(GcpInstanceMapping, VmInstanceMappingBase):
    def _get_instance(self, instance_name: str) -> GcpRemoteShellProxy:
        return GcpRemoteShellProxy(instance_name, self._session, **self._kwargs)
