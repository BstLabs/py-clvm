# -*- coding: utf-8 -*- #

from typing import Iterator, Iterable, AnyStr, Generator, Tuple, Union, Dict

from .session_azure import get_session, AzureSession

from instances_map_abc.vm_instance_mapping import VmInstanceMappingBase
from instances_map_abc.vm_instance_proxy import VmInstanceProxy
from .azure_instance_proxy import AzureInstanceProxy, AzureRemoteShellProxy


class AzureComputeAllInstancesData:
    """
    Derives all the instance data for further use.
    """

    def __init__(self, **kwargs) -> None:
        self._session = get_session(**kwargs)  # TODO get session out of here
        self._client = self._session.get_client()
        self._location = self._session.get_location()
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
        instances = []
        for _, instance_data in self._session.instances.items():
            instance_details = self._client.virtual_machines.get(
                instance_data["resource_group"],
                instance_data["instance_name"],
                expand="instanceView",
            )
            instances.append(
                (
                    instance_data["instance_id"],
                    self._get_instance_name(instance_details.tags) or instance_data["instance_name"],
                    instance_details.instance_view.statuses[1].display_status,
                )
            )
        return instances

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
        self._client = self._session.get_client()
        self._kwargs = kwargs

    def __getitem__(self, instance_name: str) -> AzureInstanceProxy:
        return self._get_instance(instance_name=instance_name)

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

    def _get_instance(self, instance_name: str) -> AzureInstanceProxy:
        return AzureInstanceProxy(
            instance_name=instance_name,
            session=self._session,
            **self._kwargs,
        )

    # def _get_instance_id(self, instance_name: str) -> str:
    #     instance_details = self._client.describe_instances(
    #         Filters=[
    #             {
    #                 "Name": "tag:Name",  # as long as you are following the convention of putting Name in tags
    #                 "Values": [
    #                     instance_name,
    #                 ],
    #             },
    #         ],
    #     )
    #     return instance_details["Reservations"][0]["Instances"][0]["InstanceId"]


class AzureRemoteShellMapping(AzureInstanceMapping, VmInstanceMappingBase):
    def _get_instance(self, instance_name: str) -> AzureRemoteShellProxy:
        return AzureRemoteShellProxy(instance_name, self._session)
