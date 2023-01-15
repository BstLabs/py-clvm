# -*- coding: utf-8 -*- #

import importlib
import json
import os
from collections import defaultdict
from typing import Any, Dict, Tuple

from _common.azure_rest_api import AzureRestApi
from azure.core.exceptions import ClientAuthenticationError
from singleton_decorator import singleton

from pyclvm.login import _login_azure


@singleton
class AzureSession:
    """
    Azure session class
    """

    def __init__(self, **kwargs):
        importlib.reload(json)
        self._profile = self._zone = kwargs.get("profile", None)  # TODO handle profiles
        self._login(**kwargs)
        self._location = kwargs.get(
            "location", os.getenv("AZURE_DEFAULT_LOCATION", "westeurope")
        )
        try:
            self._instances = self._get_instances()
        except ClientAuthenticationError:
            self._login(**{**kwargs, **{"expired": True}})
            self._instances = self._get_instances()

    def _login(self, **kwargs):
        (
            self._credentials,
            self._subscription_name,
            self._subscription_id,
        ) = _login_azure(**kwargs)

    # ---
    def _get_instances(self) -> Dict:
        rest_client = AzureRestApi(
            credentials=self._credentials, subscription_id=self._subscription_id
        )
        _instances = rest_client.list_of_vm_instances(_filter={"statusOnly": "true"})

        instances = defaultdict()
        for instance in _instances:
            resource_group = instance["id"].split("/")[4]
            instances[f"{instance['name']}"] = {
                "instance_id": instance["properties"]["vmId"],
                "resource_group": resource_group,
                "location": instance["location"],
                "instance_name": instance["name"],
                "state": instance["properties"]["instanceView"]["statuses"][1][
                    "displayStatus"
                ],
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


def get_session(**kwargs) -> AzureSession:
    return AzureSession(**kwargs)
