# -*- coding: utf-8 -*- #

from typing import Final, Dict, List, Any

from abc import ABCMeta, abstractmethod, abstractproperty, abstractstaticmethod
# ---
import importlib
import json
import os
import sys
from typing import Iterable, Any

# ---
from google.oauth2 import service_account
from google.api_core.extended_operation import ExtendedOperation
from google.cloud import compute_v1
import google.auth
import google.auth.exceptions
import google.auth.transport.requests


# https://cloud.google.com/docs/authentication/end-user
# https://cloud.google.com/docs/authentication/production


# ---
class Instance(metaclass=ABCMeta):
    """
    Abstract GCP VM instance class
    """
    # ---
    @abstractmethod
    def list_all_instances(self) -> Any:
        pass

    @abstractmethod
    def stop_instance(self, instance: str) -> Any:
        pass

    @abstractmethod
    def start_instance(self, instance: str) -> Any:
        pass

    @abstractmethod
    def reboot_instance(self, instance: str) -> Any:
        pass

    @abstractmethod
    def reset_instance(self, instance: str) -> Any:
        pass

    @abstractmethod
    def suspend_instance(self, instance: str) -> Any:
        pass

    @abstractmethod
    def resume_instance(self, instance: str) -> Any:
        pass


# ---
class GcpInstance(Instance):
    """
    GCP instance class
    """
    def __init__(self):
        creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        if creds is not None:
            self._credentials = service_account.Credentials.from_service_account_file(
                filename=creds,
                scopes=scopes,
            )
            _creds = json.load(open(creds, "rb"))
            self.project = _creds["project_id"]
            self.account_id = _creds["client_id"]
        else:
            self._credentials, self.project = google.auth.default(scopes=scopes)
            self.authed_session = google.auth.transport.requests.AuthorizedSession(self._credentials)
            self.account_id = self._credentials.client_id
        self.zone = "europe-west2-b"
        self.client = compute_v1.InstancesClient(credentials=self._credentials)

# ---
    def _get_client(self) -> compute_v1.InstancesClient:
        """
        Returns a GCP Compute client
        Returns:

        """
        return self.client

    # ---
    def list_all_instances(self) -> Iterable[compute_v1.Instance]:
        """
        Returns a dictionary of all instances present in a project, grouped by their zone.

        Returns:
            An iterable collections of Instance objects as values.
        """
        request = compute_v1.AggregatedListInstancesRequest()
        request.project = self.project
        # Use the `max_results` parameter to limit the number of results that the API returns per response page.
        request.max_results = 50
        # --- gcloud auth login --update-adc
        return self.client.aggregated_list(request=request)

    # ---
    @staticmethod
    def wait_for_operation(
            operation: compute_v1.Operation, project_id: str
    ) -> compute_v1.Operation:
        """
        This method waits for an operation to be completed. Calling this function
        will block until the operation is finished.

        Args:
            operation: The Operation object representing the operation you want to
                wait on.
            project_id: project ID or project number of the Cloud project you want to use.

        Returns:
            Finished Operation object.
        """
        kwargs = {"project": project_id, "operation": operation.name}
        if operation.zone:
            client = compute_v1.ZoneOperationsClient()
            # Operation.zone is a full URL address of a zone, so we need to extract just the name
            kwargs["zone"] = operation.zone.rsplit("/", maxsplit=1)[1]
        elif operation.region:
            client = compute_v1.RegionOperationsClient()
            # Operation.region is a full URL address of a region, so we need to extract just the name
            kwargs["region"] = operation.region.rsplit("/", maxsplit=1)[1]
        else:
            client = compute_v1.GlobalOperationsClient()
        return client.wait(**kwargs)

    # ---
    @staticmethod
    def _wait_for_extended_operation(
            operation: ExtendedOperation,
            verbose_name: str = "operation",
            timeout: int = 300
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
    def stop_instance(self, instance: str) -> Any:
        """
        Stops the instance
        Args:
            instance: Name of the instance
        Returns:
            (str) Status of operation
        """
        operation = self.client.stop(project=self.project, zone=self.zone, instance=instance)
        return self._wait_for_extended_operation(operation, "instance stopping")

    # ---
    def start_instance(self, instance: str) -> Any:
        """
        Stops the instance
        Args:
            instance: Name of the instance
        Returns:
            (str) Status of operation
        """
        operation = self.client.start(project=self.project, zone=self.zone, instance=instance)
        return self._wait_for_extended_operation(operation, "instance starting")

    # ---
    def reset_instance(self, instance: str) -> Any:
        """
        Resets the instance
        Args:
            instance: Name of the instance
        Returns:
            (str) Status of operation
        """
        operation = self.client.reset(project=self.project, zone=self.zone, instance=instance)
        return self._wait_for_extended_operation(operation, "instance resetting")

    # ---
    def reboot_instance(self, instance: str) -> Any:
        """
        Resets the instance
        Args:
            instance: Name of the instance
        Returns:
            (str) Status of operation
        """
        return self.reset_instance(instance=instance)

    # ---
    def suspend_instance(self, instance: str) -> Any:
        """
        Suspends the instance
        Args:
            instance: Name of the instance
        Returns:
            (str) Status of operation
        """
        operation = self.client.suspend(project=self.project, zone=self.zone, instance=instance)
        return self._wait_for_extended_operation(operation, "instance suspending")

    # ---
    def resume_instance(self, instance: str) -> Any:
        """
        Resumes the instance
        Args:
            instance: Name of the instance
        Returns:
            (str) Status of operation
        """
        operation = self.client.resume(project=self.project, zone=self.zone, instance=instance)
        return self._wait_for_extended_operation(operation, "instance resuming")


# -------------------------
def main():
    vmi = GcpInstance()
    ls = vmi.list_all_instances()
    print(ls)



# -------------------------
if __name__ == "__main__":
    main()