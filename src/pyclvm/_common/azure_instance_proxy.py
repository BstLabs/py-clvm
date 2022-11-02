# -*- coding: utf-8 -*- #

import contextlib
import enum
import json
import os
import signal
import socket
import subprocess
from distutils.util import strtobool
from time import sleep, time
from typing import Any, Generator, Iterable, NewType, Optional, Union

from _common.azure_rest_api import AzureRestApi
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
        self._instance = self._session.instances[instance_name]
        self._wait_for_queue = kwargs.get("wait", "yes")
        self._rest_api = AzureRestApi(
            credentials=session.credentials,
            subscription_id=session.subscription,
        )

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
        vm_operation = self._rest_api.vm_start(
            resource_group_name=self._instance["resource_group"].lower(),
            vm_instance_name=self._instance["instance_name"],
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
        vm_operation = self._rest_api.vm_deallocate(
            resource_group_name=self._instance["resource_group"].lower(),
            vm_instance_name=self._instance["instance_name"],
        )
        if wait:
            self._wait_for_extended_operation("VM deallocated")
        return vm_operation

    @property
    def state(self) -> Optional[str]:
        instance_details = self._rest_api.vm_instance_view(
            self._instance["resource_group"].lower(),
            self._instance["instance_name"],
        )
        with contextlib.suppress(IndexError):
            return instance_details["statuses"][1]["displayStatus"]

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
        port = next_free_port()
        exec_command(
            build_azure_tunnel(self, port, **kwargs), port, *commands, **kwargs
        )

    # ---
    @property
    def session(self):
        return self._session


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


# ---
def build_azure_tunnel(
    instance: AzureRemoteShellProxy, port: int, **kwargs
) -> subprocess:
    instance_name = instance.name
    resource_group = instance.session.instances[instance_name]["resource_group"].lower()
    subscription = instance.session.subscription

    cmd = [
        "az.cmd" if _OS == "Windows" else "az",
        "network",
        "bastion",
        "tunnel",
        "--port",
        str(port),
        "--resource-port",
        "22",
        "--name",
        f"{resource_group}-vpc-bastion",  # TODO Retrieve Bastion name via REST API
        "--resource-group",
        resource_group,
        "--target-resource-id",
        f"/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{instance_name}",
        "--only-show-errors",
    ]
    tunnel_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL)
    sleep(3)  # Wait until tunnel to build
    return tunnel_proc


def grace_kill(proc: subprocess, sig: signal) -> enum:
    # TODO Add any clearance procedures if necessary (e.g. stop VM)
    if _OS == "Windows":
        os.kill(proc.pid, sig)
    else:
        os.killpg(os.getpgid(proc.pid), sig)
    return signal.getsignal(sig)


def create_socket(tunnel_proc: subprocess, port: int, **kwargs) -> None:
    account = kwargs.get("account")
    key = kwargs.get("key")
    cmd = [
        "ssh",
        "-p",
        f"{port}",
        "-i",
        os.path.normpath(f"{key}"),
        f"{account}@localhost",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "StrictHostKeyChecking=no",
        "-W",
        "localhost:22",
    ]
    if _OS != "Windows":
        cmd.extend(
            [
                "-o",
                "ConnectTimeout=3",
            ]
        )

    cnt = 10
    while cnt > 0:
        enter_sec = int(time())
        subprocess.run(cmd)
        if int(time() - enter_sec) > 5:
            break
        sleep(3)
        cnt -= 1

    signal.signal(signal.SIGTERM, grace_kill(tunnel_proc, signal.SIGTERM))


def exec_command(
    tunnel_proc: subprocess,
    port: int,
    *commands: Union[str, Iterable],
    **kwargs: str,
) -> None:
    account = kwargs.get("account")
    key = kwargs.get("key")
    cmd = [
        "ssh",
        "-p",
        str(port),
        "-i",
        os.path.normpath(key),
        f"{account}@localhost",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "StrictHostKeyChecking=no",
    ]
    if _OS != "Windows":
        cmd.extend(
            [
                "-o",
                "ConnectTimeout=5",
            ]
        )

    _commands = " ".join(*commands) if len(commands) > 0 else ""
    if _commands:
        cmd.append(f"cd $HOME && {_commands}")

    cnt = 10
    while cnt > 0:
        enter_time = time()
        subprocess.run(cmd)
        lag = time() - enter_time
        if lag < 5.001 or lag > 5.02:  # TODO Fix it. It relies on SSH ConnectTimeout.
            break
        sleep(1)
        cnt -= 1

    signal.signal(signal.SIGTERM, grace_kill(tunnel_proc, signal.SIGTERM))


def ssh_connection_std_output(instance: AzureRemoteShellProxy, **kwargs) -> None:
    port = next_free_port()
    create_socket(
        tunnel_proc=build_azure_tunnel(instance, port, **kwargs),
        port=port,
        **kwargs,
    )
