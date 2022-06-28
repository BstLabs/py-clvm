# -*- coding: utf-8 -*- #

from typing import Iterator, Iterable, AnyStr, Generator, Tuple, Union, Dict

from .session_azure import get_session, AzureSession


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
        for instance in self._client.virtual_machines.list_all():
            # TODO to come out what to do with "resource_group" and "location"
            resource_group = instance.id.split("/")[4]
            location = instance.location
            instance_details = self._client.virtual_machines.get(resource_group, instance.name, expand="instanceView")

            instances.append((
                instance.vm_id,
                self._get_instance_name(instance_details.tags) or instance.name,
                instance_details.instance_view.statuses[1].display_status,
            ))

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
