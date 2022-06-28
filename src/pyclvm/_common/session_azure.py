# -*- coding: utf-8 -*- #

import os
from typing import Any, Union, Tuple

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.subscription import SubscriptionClient

from singleton_decorator import singleton


@singleton
class AzureSession:
    """
    GCP instance class
    """

    def __init__(self, **kwargs):
        self._profile = self._zone = kwargs.get("profile", None)  # TODO handle profiles
        self._credentials = DefaultAzureCredential()
        self._subscription_name, self._subscription_id = self._get_subscription()
        self._client = ComputeManagementClient(
            credential=self._credentials,
            subscription_id=self._subscription_id,
        )
        self._location = kwargs.get(
            "location", os.getenv("AZURE_DEFAULT_LOCATION", "westeurope")
        )
        self.resource_group = kwargs.get(
            "resource_group", os.getenv("AZURE_RESOURCE_GROUP", "")
        )

    # ---
    def _get_subscription(self) -> Tuple[str, str]:
        subscription_client = SubscriptionClient(self._credentials)
        for r in subscription_client.subscriptions.list():
            if r.display_name:
                return r.display_name, r.subscription_id

    # ---
    @property
    def subscription(self) -> Any:
        return self._subscription_id

    # ---
    @property
    def subscription_name(self) -> Any:
        return self._subscription_name

    # ---
    def get_client(self) -> ComputeManagementClient:
        """
        Returns a GCP Compute client
        Returns:

        """
        return self._client

    @property
    # ---
    def client(self) -> ComputeManagementClient:
        """
        Returns a GCP Compute client
        Returns:

        """
        return self._client

    # # ---
    # def is_expired(self) -> bool:
    #     return self._expired
    #
    # # ---
    # def is_verified(self) -> Union[bool, str, None]:
    #     return self._verify

    # ---
    def get_location(self) -> Union[bool, str, None]:
        return self._location

    # ---
    @property
    def location(self) -> Union[Any, str, None]:
        return self._location

    # ---
    def set_location(self, localtion: str) -> None:
        self._location = localtion


def get_session(**kwargs) -> AzureSession:
    return AzureSession(**kwargs)
