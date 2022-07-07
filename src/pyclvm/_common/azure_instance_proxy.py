# -*- coding: utf-8 -*- #

import os
import signal
import socket
import subprocess
import sys
from select import select
from threading import Thread, ThreadError
from time import sleep
from typing import Any, Iterable, Union

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
            self._instance["resource_group"].lower(), self._instance["instance_name"]
        )

    # ---
    def stop(self) -> Union[Any, None]:
        """
        Stops the vm
        """
        return self._client.virtual_machines.begin_deallocate(
            self._instance["resource_group"].lower(), self._instance["instance_name"]
        )

    @property
    def state(self) -> str:
        instance_details = self._client.virtual_machines.get(
            self._instance["resource_group"].lower(),
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

    def __init__(self, instance: AzureRemoteShellProxy, port: int):
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

        try:
            cmd = [
                "az",
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
        except (ThreadError, RuntimeError):
            pass

    def stop(self):
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
        **kwargs,
    ):
        super().__init__()
        self._instance = instance
        self._connector = connector
        self._commands = commands
        self._port = port
        self._account = kwargs.get("account")
        self._key = kwargs.get("key")

        if not self._account or not self._key:
            raise RuntimeError(
                "\n-----------\nSpecify account=account_name or/and key=/path/to/ssh/key/file\n"
                "e.g. clvm connect vm-instance-name account=username key=/path/to/ssh/key platform=azure\n"
            )

    # ---
    def run(self):
        sleep(5)
        command = " ".join(*self._commands) if len(self._commands) > 0 else ""
        try:
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
        except (ThreadError, RuntimeError):
            pass


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

    # ---
    def run(self):
        sleep(5)
        TcpProxy("127.0.0.1", self._port, self._connector)()
        raise ThreadError()


# ---
class TcpProxy:
    BUFFER_SIZE = 4096

    def __init__(self, dst_host, dst_port, connector: AzureRemoteConnector):
        self._dst = (dst_host, dst_port)
        self._input_list = []

        self._proxy_in, self._proxy_out = self._setup_proxy()
        self._target = self._setup_target()

        self._connector = connector

    def _setup_target(self):
        try:
            target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target.connect(self._dst)
            self._input_list.append(target)
            return target
        except ConnectionRefusedError as e:
            print(e)
            raise KeyboardInterrupt()
            # sys.exit(-1)

    def _setup_proxy(self):
        proxy_in = sys.stdin
        proxy_out = sys.stdout
        self._input_list.append(proxy_in)
        return proxy_in, proxy_out

    def __call__(self):
        while True:
            channel_rlist, _, _ = select(self._input_list, [], [])

            for channel in channel_rlist:
                if channel == self._proxy_in:
                    data = channel.buffer.read1()
                    if len(data):
                        self._send(data)
                elif channel == self._target:
                    _data = channel.recv(self.BUFFER_SIZE)
                    if len(_data) == 0:
                        self._close(channel)
                        break
                    else:
                        self._receive(_data)

    def _close(self, _channel):
        self._input_list.remove(_channel)
        self._target.close()

    def _send(self, data):
        try:
            self._target.send(data)
        except OSError as e:
            print(e)
            raise KeyboardInterrupt()
            # sys.exit(-1)

    def _receive(self, data):
        self._proxy_out.buffer.write(data)
        self._proxy_out.buffer.flush()

    def __del__(self):
        self._connector.stop()


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
