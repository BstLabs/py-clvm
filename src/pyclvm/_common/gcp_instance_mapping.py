# -*- coding: utf-8 -*- #

import os
from typing import Iterator, Iterable, AnyStr, Generator, Tuple, Union

from .session_gcp import get_session, GcpSession
from google.cloud import compute_v1

from instances_map_abc.vm_instance_mapping import VmInstanceMappingBase
from instances_map_abc.vm_instance_proxy import VmInstanceProxy
from .gcp_instance_proxy import GcpInstanceProxy, GcpRemoteShellProxy


class GcpComputeAllInstancesData:
    """
    Derives all the instance data for further use.
    """
    def __init__(self, **kwargs) -> None:
        self._session = get_session(**kwargs)
        self._client = self._session.get_client()
        self._zone = kwargs.get(
            "zone", os.getenv("CLOUDSDK_COMPUTE_ZONE", "europe-west2-b")
        )
        self._instances_data = self._instances()

    # ---
    def get_session(self) -> GcpSession:
        return self._session

    # ---
    def _instances(self) -> Iterable:
        request = compute_v1.AggregatedListInstancesRequest()
        request.project = self._session.project_id
        # Use the `max_results` parameter to limit the number of results that the API returns per response page.
        # request.max_results = 50
        # _instances = filter(lambda x: (x[0] == f"zones/{self._zone}"),
        #              self._client.aggregated_list(request=request))
        _instances = []
        for zone, instances_in_zone in self._client.aggregated_list(request=request):
            if f"zones/{self._zone}" == zone:
                _instances = instances_in_zone.instances

        return [
            (
                _instance.id,
                self._get_instance_name(_instance.tags) or _instance.name,
                _instance.status,
            )
            for _instance in _instances
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
    def __init__(self, session: GcpSession) -> None:
        self._session = session
        self._client = self._session.get_client()

    def __getitem__(self, name: str) -> VmInstanceProxy:
        instance_id = self._get_instance_id(name)
        return self._get_instance(instance_id)

    def __iter__(self) -> Iterator:
        instances = (
            r["Instances"][0] for r in self._client.describe_instances()["Reservations"]
        )
        for instance in instances:
            yield self._get_instance(instance["InstanceId"])

    def __len__(self) -> int:
        return sum(1 for _ in self)

    def keys(self) -> Generator[str, None, None]:
        for instance in self:
            yield instance.name

    def values(self) -> Generator[str, None, None]:
        yield from self

    def items(self) -> Generator[Tuple[str, str], None, None]:
        yield from zip(self.keys(), self.values())

    def _get_instance(self, instance_id: str) -> GcpInstanceProxy:
        return GcpInstanceProxy()

    def _get_instance_id(self, instance_name: str) -> str:
        instance_details = self._client.describe_instances(
            Filters=[
                {
                    "Name": "tag:Name",  # as long as you are following the convention of putting Name in tags
                    "Values": [
                        instance_name,
                    ],
                },
            ],
        )
        return instance_details["Reservations"][0]["Instances"][0]["InstanceId"]


class GcpRemoteShellMapping(GcpInstanceMapping, VmInstanceMappingBase):
    def _get_instance(self, instance_id: str) -> GcpRemoteShellProxy:
        return GcpRemoteShellProxy()
