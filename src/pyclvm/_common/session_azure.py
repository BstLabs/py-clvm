# -*- coding: utf-8 -*- #

import importlib
import json
import os
from collections import defaultdict
from typing import Any, Dict, Tuple

from azure.mgmt.compute import ComputeManagementClient
from singleton_decorator import singleton

from pyclvm.login import _login_azure
from _common.azure_rest_api import AzureRestApi


@singleton
class AzureSession:
    """
    Azure session class
    """

    def __init__(self, **kwargs):
        importlib.reload(json)
        self._profile = self._zone = kwargs.get("profile", None)  # TODO handle profiles
        (
            self._credentials,
            self._subscription_name,
            self._subscription_id,
        ) = _login_azure(**kwargs)
        self._client = ComputeManagementClient(
            credential=self._credentials,
            subscription_id=self._subscription_id,
        )
        self._location = kwargs.get(
            "location", os.getenv("AZURE_DEFAULT_LOCATION", "westeurope")
        )
        self._instances = self._get_instances()

    # ---
    def _get_instances(self) -> Dict:
        r = AzureRestApi(credentials=self._credentials, subscription_id=self._subscription_id)
        _instances = r.list_of_vm_instances(_filter={"statusOnly": "true"})

        instances = defaultdict()
        for instance in _instances:
            resource_group = instance["id"].split("/")[4]
            instances[f"{instance['name']}"] = {
                "instance_id": instance["properties"]["vmId"],
                "resource_group": resource_group,
                "location": instance["location"],
                "instance_name": instance["name"],
                "state": instance["properties"]["instanceView"]["statuses"][1]["displayStatus"]
            }
        return dict(instances)

    # ---
    @property
    def instances(self) -> Dict:
        """
        Returns Azure VM instances
        """
        return self._instances

    # ---
    def _get_subscription(self) -> Tuple[str, str]:
        return self._subscription_name, self._subscription_id

    # ---
    @property
    def subscription(self) -> Any:
        """
        Returns Azure Subscription name
        """
        return self._subscription_id

    @property
    def credentials(self) -> Any:
        """
        Returns Azure Subscription name
        """
        return self._credentials

    # ---
    @property
    def subscription_name(self) -> Any:
        """
        Returns Azure Subscription name
        """
        return self._subscription_name

    # ---
    def get_client(self) -> ComputeManagementClient:
        """
        Returns Azure Compute client
        """
        return self._client

    @property
    # ---
    def client(self) -> ComputeManagementClient:
        """
        Returns Azure Compute client
        """
        return self._client


def get_session(**kwargs) -> AzureSession:
    return AzureSession(**kwargs)
