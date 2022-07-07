# -*- coding: utf-8 -*- #

import subprocess
import sys
from distutils.util import strtobool
from typing import Any, Iterable, Union

from google.api_core.extended_operation import ExtendedOperation

from .session_gcp import GcpSession


class GcpInstanceProxy:
    def __init__(
        self,
        instance_name: str,
        session: GcpSession,
        **kwargs: str,
    ) -> None:
        self._session = session
        self._instance_name = instance_name
        self._client = session.get_client()
        self._instance = self._client.get(
            project=self._session.project_id,
            zone=self._session.zone,
            instance=self._instance_name,
        )

    # ---
    @staticmethod
    def _wait_for_extended_operation(
        operation: ExtendedOperation,
        verbose_name: str = "operation",
        timeout: int = 300,
    ) -> Any:
        """
        This method will wait for the extended (long-running) operation to
        complete. If the operation is successful, it will return its result.
        If the operation ends with an error, an exception will be raised.
        If there were any warnings during the execution of the operation
        they will be printed to sys.stderr.

        Args:
            operation: a long-running operation you want to wait on.
            verbose_name: (optional) a more verbose name of the operation,
                used only during error and warning reporting.
            timeout: how long (in seconds) to wait for operation to finish.
                If None, wait indefinitely.

        Returns:
            Whatever the operation.result() returns.

        Raises:
            This method will raise the exception received from `operation.exception()`
            or RuntimeError if there is no exception set, but there is an `error_code`
            set for the `operation`.

            In case of an operation taking longer than `timeout` seconds to complete,
            a `concurrent.futures.TimeoutError` will be raised.
        """
        result = operation.result(timeout=timeout)

        if operation.error_code:
            print(
                f"Error during {verbose_name}: [Code: {operation.error_code}]: {operation.error_message}",
                file=sys.stderr,
            )
            print(f"Operation ID: {operation.name}")
            raise operation.exception() or RuntimeError(operation.error_message)

        if operation.warnings:
            print(f"Warnings during {verbose_name}:\n", file=sys.stderr)
            for warning in operation.warnings:
                print(f" - {warning.code}: {warning.message}", file=sys.stderr)

        return result

    # ---
    def start(self, wait: bool = True) -> Union[Any, None]:
        """
        Starts the vm

        :return: None
        """
        operation = self._client.start(
            project=self._session.project_id,
            zone=self._session.zone,
            instance=self._instance_name,
        )
        return (
            self._wait_for_extended_operation(operation, "instance stopping")
            if wait
            else None
        )

    # ---
    def stop(self, wait: bool = True) -> Union[Any, None]:
        """
        Stops the vm

        :return: None
        """
        operation = self._client.stop(
            project=self._session.project_id,
            zone=self._session.zone,
            instance=self._instance_name,
        )
        return (
            self._wait_for_extended_operation(operation, "instance stopping")
            if wait
            else None
        )

    @property
    def state(self) -> str:
        return self._instance.status

    @property
    def id(self) -> str:
        return str(self._instance.id)

    @property
    def name(self):
        try:
            return self._instance.tags.name
        except AttributeError:
            return self._instance.name


class GcpRemoteShellProxy(GcpInstanceProxy):
    def __init__(self, instance_name: str, session: GcpSession, **kwargs) -> None:
        super().__init__(instance_name, session, **kwargs)
        self._session = session
        self._proxy_client = (
            None  # TODO realise proxy client (SSH or any other remote call)
        )

    # ---
    def execute(self, *commands: Union[str, Iterable], **kwargs) -> Any:
        command = f"--command={' '.join(*commands)}" if len(*commands) > 0 else ""
        tunnel_through_iap = strtobool(kwargs.get("iap", "yes"))
        dry_run = strtobool(kwargs.get("dry_run", "no"))
        account = kwargs.get("account")

        cmd = [
            "gcloud",
            "compute",
            "ssh",
            f"--project={self._session.project}",
            f"--zone={self._session.zone}",
            self._instance_name,
        ]
        if command:
            cmd.append(command)
        if tunnel_through_iap:
            cmd.append("--tunnel-through-iap")
        if account:
            cmd.append(f"--account={account}")
        if dry_run:
            cmd.append("--dry-run")

        return subprocess.run(cmd, capture_output=kwargs.get("capture_output", False))

    # ---
    @property
    def session(self):
        return self._session
