# -*- coding: utf-8 -*- #
import os
from time import sleep
import subprocess
from multiprocessing import Process, ProcessError
from typing import Any, Iterable, Union
import signal

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
            for _key, _value in self._instance.tags.items():
                if _key.upper() == "NAME":
                    return _value
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
        _connector = AzureRemoteConnector(self)
        _socket = AzureRemoteSocket(self, _connector, *commands, **kwargs)
        _connector.start()
        _socket.start()
        print("Socket started")
        _connector.join()
        _socket.join()

    # ---
    @property
    def session(self):
        return self._session


# ---
class AzureRemoteConnector(Process):
    """
    Azure remote connector class
    """

    def __init__(self, instance: AzureRemoteShellProxy):
        super().__init__()
        self._instance = instance
        self._proc = None

    # ---
    def run(self):
        resource_group = self._instance.session.instances[self._instance.name][
            "resource_group"
        ]
        subscription = self._instance.session.subscription
        instance_name = self._instance.name
        self._proc = subprocess

        try:
            cmd = [
                "az",
                "network",
                "bastion",
                "tunnel",
                "--port",
                "22026",
                "--resource-port",
                "22",
                "--name",
                f"{resource_group}-vpc-bastion",
                "--resource-group",
                resource_group,
                "--target-resource-id",
                f"/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{instance_name}",
            ]
            self._proc = subprocess.call(cmd)
        except (ProcessError, RuntimeError):
            raise

    # def __del__(self):
    #     self.kill()


# ---
class AzureRemoteSocket(Process):
    """
    Azure remote socket class
    """

    def __init__(
        self,
        instance: AzureRemoteShellProxy,
        connector: AzureRemoteConnector,
        *commands: Union[str, Iterable],
        **kwargs,
    ):
        super().__init__()
        self._instance = instance
        self._connector = connector
        self._commands = commands

    # ---
    def run(self):
        sleep(5)
        command = (
            " ".join(self._commands[0]) if len(self._commands) > 0 else ""
        )  # TODO check "commands" tuple
        try:
            cmd = [
                "ssh",
                "-p",
                "22026",
                "-i",
                os.path.normpath(f"{os.getenv('HOME')}/.ssh/git.key"),
                "dmitro@localhost",
                "-o",
                "UserKnownHostsFile=/dev/null",
                "-o",
                "StrictHostKeyChecking=no",
                command,
            ]
            subprocess.run(cmd)
            os.killpg(os.getpgid(self._connector.pid), signal.SIGTERM)
            self.close()
        except (ProcessError, RuntimeError):
            raise
