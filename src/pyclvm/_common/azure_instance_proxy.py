# -*- coding: utf-8 -*- #

import contextlib
import json
import os
import signal
import socket
import subprocess
import sys
from distutils.util import strtobool
from threading import Thread, ThreadError
from time import sleep
from typing import Any, Generator, Iterable, NewType, Optional, Union

from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.storage import StorageManagementClient
from azure.storage.queue import (
    BinaryBase64DecodePolicy,
    BinaryBase64EncodePolicy,
    QueueClient,
)

from pyclvm.plt import _get_os

from .session_azure import AzureSession

_OS = _get_os()

Status = NewType("status", str)
status = Status("down")


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
        self._wait_for_queue = kwargs.get("wait", "yes")

    # ---
    def _wait_for_extended_operation(self, state: str, timeout: int = 300) -> None:
        while timeout:
            if self.state == state:
                break
            sleep(1)
            timeout -= 1

    # ---
    def start(self, wait: bool = True) -> Any:
        """
        Starts the vm
        """
        vm_operation = self._client.virtual_machines.begin_start(
            self._instance["resource_group"].lower(), self._instance["instance_name"]
        )
        if wait:
            self._wait_for_extended_operation("VM running")
            if strtobool(self._wait_for_queue):
                self._wait_runtime(timeout=30)

        return vm_operation

    # ---
    def stop(self, wait: bool = True) -> Any:
        """
        Stops the vm
        """
        vm_operation = self._client.virtual_machines.begin_deallocate(
            self._instance["resource_group"].lower(), self._instance["instance_name"]
        )
        if wait:
            self._wait_for_extended_operation("VM deallocated")
        return vm_operation

    @property
    def state(self) -> Optional[str]:
        instance_details = self._client.virtual_machines.get(
            self._instance["resource_group"].lower(),
            self._instance["instance_name"],
            expand="instanceView",
        )
        with contextlib.suppress(IndexError):
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
    def _sub(self, timeout: Optional[float] = None) -> Status:
        global status
        storage_client = StorageManagementClient(
            self._session.credentials, self._session.subscription
        )
        resource_group = self._instance_name[: self._instance_name.index("-desktop")]
        rg_availability = storage_client.storage_accounts.check_name_availability(
            {"name": resource_group}
        )
        if not rg_availability.reason:
            return status

        service_account = resource_group.replace("-", "")

        try:

            def storage_keys() -> Generator:
                for key in storage_client.storage_accounts.list_keys(
                    resource_group, service_account
                ).keys:
                    yield key.value

            connection_string = f"DefaultEndpointsProtocol=https;AccountName={service_account};AccountKey={next(storage_keys())};EndpointSuffix=core.windows.net"

            queue_name = self._instance_name
            queue_client = QueueClient.from_connection_string(
                connection_string,
                queue_name,
                message_encode_policy=BinaryBase64EncodePolicy(),
                message_decode_policy=BinaryBase64DecodePolicy(),
            )
            messages = queue_client.peek_messages()
            messages_content = [
                {"id": message.id, "content": message.content} for message in messages
            ]

            for message in messages_content:
                try:
                    content = json.loads(message["content"])
                    if self._instance_name == content["vm-id"].split("/")[8]:
                        status = content["status"]
                except KeyError:
                    return status

        except ResourceNotFoundError:
            return status

        return status

    # ---
    def _wait_runtime(self, timeout: int) -> None:
        while timeout > 0:
            timeout -= 1
            if "up" == self._sub():
                return
            print(".", end="")

        print(
            "\n------\nQueue service is not adjusted. You can continue, but it takes time to start an VM instance.\n"
        )


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
        _port = next_free_port()
        _connector = AzureRemoteConnector(self, _port)
        _executor = AzureRemoteExecutor(self, _connector, _port, *commands, **kwargs)
        _connector.start()
        _executor.start()
        _connector.join()
        _executor.join()

    # ---
    @property
    def session(self):
        return self._session


# ---
class AzureRemoteConnector(Thread):
    """
    Azure remote connector class
    """

    def __init__(self, instance: AzureRemoteShellProxy, port: int, **kwargs) -> None:
        super().__init__()
        self._instance = instance
        self._proc = None
        self._port = port

    # ---
    def run(self):
        resource_group = self._instance.session.instances[self._instance.name][
            "resource_group"
        ].lower()
        subscription = self._instance.session.subscription
        instance_name = self._instance.name
        self._proc = subprocess

        with contextlib.suppress(ThreadError, RuntimeError):
            cmd = [
                "az.cmd" if _OS == "Windows" else "az",
                "network",
                "bastion",
                "tunnel",
                "--port",
                str(self._port),
                "--resource-port",
                "22",
                "--name",
                f"{resource_group}-vpc-bastion",
                "--resource-group",
                resource_group,
                "--target-resource-id",
                f"/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{instance_name}",
                "--only-show-errors",
            ]
            self._proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL)
            raise ThreadError

    def stop(self):
        if _OS == "Windows":
            os.kill(self._proc.pid, signal.SIGTERM)
        else:
            os.killpg(os.getpgid(self._proc.pid), signal.SIGTERM)


# ---
class AzureRemoteExecutor(Thread):
    """
    Azure remote socket class
    """

    def __init__(
        self,
        instance: AzureRemoteShellProxy,
        connector: AzureRemoteConnector,
        port: int,
        *commands: Union[str, Iterable],
        **kwargs: str,
    ):
        super().__init__()
        self._instance = instance
        self._connector = connector
        self._commands = commands
        self._port = port
        self._account = kwargs.get("account")
        self._key = kwargs.get("key")

        if not self._account or not self._key:
            print(
                "\n-----------\nSpecify account=account_name or/and key=/path/to/ssh/key/file\n"
                "e.g.\n\tclvm connect vm-instance-name account=username key=/path/to/ssh/key platform=azure\n"
            )
            sys.exit(-1)

    # ---
    def run(self):
        sleep(5)
        command = " ".join(*self._commands) if len(self._commands) > 0 else ""
        with contextlib.suppress(ThreadError, RuntimeError):
            cmd = [
                "ssh",
                "-p",
                str(self._port),
                "-i",
                os.path.normpath(self._key),
                f"{self._account}@localhost",
                "-o",
                "UserKnownHostsFile=/dev/null",
                "-o",
                "StrictHostKeyChecking=no",
            ]
            if command:
                cmd.append(command)
            subprocess.run(cmd)
            self._connector.stop()


# ---
class AzureRemoteSocket(Thread):
    """
    Azure remote socket class
    """

    def __init__(
        self,
        instance: AzureRemoteShellProxy,
        connector: AzureRemoteConnector,
        port: int,
        **kwargs,
    ):
        super().__init__()
        self._instance = instance
        self._connector = connector
        self._port = port
        self._account = kwargs.get("account")
        self._key = kwargs.get("key")

    # ---
    def run(self):
        sleep(5)  # Delay to run az tunnel
        subprocess.run(
            [
                "ssh",
                "-p",
                f"{self._port}",
                "-i",
                os.path.normpath(f"{self._key}"),
                f"{self._account}@localhost",
                "-o",
                "UserKnownHostsFile=/dev/null",
                "-o",
                "StrictHostKeyChecking=no",
                "-W",
                "localhost:22",
            ]
        )
        self._connector.stop()
        raise ThreadError()


# ---
def next_free_port(port=44500, max_port=45500):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while port <= max_port:
        try:
            sock.bind(("127.0.0.1", port))
            sock.close()
            return port
        except OSError:
            port += 1
    raise IOError("no free ports")
