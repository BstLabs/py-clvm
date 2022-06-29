# -*- coding: utf-8 -*- #

import sys
import subprocess
from typing import Any, Iterable, Union

from distutils.util import strtobool

from .session_azure import AzureSession


class AzureInstanceProxy:
    def __init__(
        self,
        instance_name: str,
        session: AzureSession,
        **kwargs: str,
    ) -> None:
        self._session = session
        self._instance_name = instance_name
        self._client = session.get_client()
        self._instance = self._session.instances[instance_name]

    # ---
    def start(self) -> Union[Any, None]:
        """
        Starts the vm
        """
        return self._client.virtual_machines.begin_start(
            self._instance["resource_group"], self._instance["instance_name"]
        )

    # ---
    def stop(self) -> Union[Any, None]:
        """
        Stops the vm
        """
        return self._client.virtual_machines.begin_deallocate(
            self._instance["resource_group"], self._instance["instance_name"]
        )

    @property
    def state(self) -> str:
        instance_details = self._client.virtual_machines.get(
            self._instance["resource_group"],
            self._instance["instance_name"],
            expand="instanceView",
        )
        return instance_details.instance_view.statuses[1].display_status

    @property
    def id(self) -> str:
        return str(self._instance["instance_id"])

    @property
    def name(self):
        try:
            return self._instance.tags.name
        except AttributeError:
            return self._instance["instance_name"]


# ---
class AzureRemoteShellProxy(AzureInstanceProxy):
    def __init__(self, instance_name: str, session: AzureSession, **kwargs) -> None:
        super().__init__(instance_name, session, **kwargs)
        self._session = session
        self._proxy_client = (
            None  # TODO realise proxy client (SSH or any other remote call)
        )

    # ---
    def execute(self, *commands: Union[str, Iterable], **kwargs) -> Any:
        ...

    # ---
    @property
    def session(self):
        return self._session
