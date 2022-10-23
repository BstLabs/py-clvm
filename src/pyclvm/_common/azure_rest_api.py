# -*- coding: utf-8 -*- #

from singleton_decorator import singleton
import json
from azure.core.credentials import AccessToken
from azure.identity import DefaultAzureCredential, AzureCliCredential
from typing import Tuple, Union, Dict, List, Optional
import requests
from base64 import b64decode


class AzureRestApi:
    """
    Base class for Azure REST API
    """
    def __init__(self, credentials: Union[DefaultAzureCredential, AzureCliCredential], subscription_id: Optional[str] = None):
        self._scope = [
            "https://management.azure.com/",
        ]
        self._token = credentials.get_token(*self._scope)
        self._base_url = "https://management.azure.com/"
        self._base_api_version = "2022-01-01"
        self._subscription_id = self._get_subscription_id(subscription_id)

    def _build_url(self, resource: str, filters: Optional[Dict] = {}) -> str:
        _filters = "".join([f"&{k}={v}" for k, v in filters.items()])
        return f"{self._base_url}/{resource}?api-version={self._base_api_version}{_filters}"

    def _get_data(self, url) -> Dict:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token.token}"
        }
        resp = requests.get(url=url, headers=headers)
        if resp.status_code != 200:
            raise RuntimeError(f"Azure REST API error: {resp.reason}, code: {resp.status_code}")
        return json.loads(resp.text)

    def _get_subscription_id(self, subscription_id: str) -> str:
        if not subscription_id:
            # TODO Realise more than one Subscriptions ID
            return next(sid["subscriptionId"] for sid in self.list_of_subscriptions())
        return subscription_id

    def list_of_subscriptions(self) -> List[Dict]:
        return self._get_data(self._build_url("subscriptions"))["value"]

    def list_of_resource_groups(self) -> List[Dict]:
        return self._get_data(
            self._build_url(
                f"subscriptions/{self._subscription_id}/resourcegroups",
            )
        )["value"]

    def list_of_vm_instances(self, _filter: Optional[Dict] = {}) -> List[Dict]:
        self._base_api_version = "2022-08-01"
        return self._get_data(
            self._build_url(
                f"subscriptions/{self._subscription_id}/providers/Microsoft.Compute/virtualMachines",
                _filter,
            )
        )["value"]
