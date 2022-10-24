# -*- coding: utf-8 -*- #

from singleton_decorator import singleton
import json
from azure.identity import DefaultAzureCredential, AzureCliCredential
from typing import Tuple, Union, Dict, List, Optional
import requests


@singleton
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

    def _get(self, url) -> Dict:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token.token}"
        }
        resp = requests.get(url=url, headers=headers)
        if resp.status_code != 200:
            raise RuntimeError(f"Azure REST API error: {resp.reason}, code: {resp.status_code}")
        return json.loads(resp.text)

    def _post(self, url) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token.token}"
        }
        resp = requests.post(url=url, headers=headers)
        if resp.status_code not in [200, 202]:
            raise RuntimeError(f"Azure REST API error: {resp.reason}, code: {resp.status_code}")
        return str(resp.elapsed)

    def _get_subscription_id(self, subscription_id: str) -> str:
        if not subscription_id:
            # TODO Realise more than one Subscriptions ID
            return next(sid["subscriptionId"] for sid in self.list_of_subscriptions())
        return subscription_id

    def list_of_subscriptions(self) -> List[Dict]:
        return self._get(self._build_url("subscriptions"))["value"]

    def list_of_resource_groups(self) -> List[Dict]:
        return self._get(
            self._build_url(
                f"subscriptions/{self._subscription_id}/resourcegroups",
            )
        )["value"]

    def list_of_vm_instances(self, _filter: Optional[Dict] = {}) -> List[Dict]:
        self._base_api_version = "2022-08-01"
        return self._get(
            self._build_url(
                f"subscriptions/{self._subscription_id}/providers/Microsoft.Compute/virtualMachines",
                _filter,
            )
        )["value"]

    def vm_instance_view(self, resource_group_name: str, vm_instance_name: str) -> Dict:
        self._base_api_version = "2022-08-01"
        return self._get(
            self._build_url(
                f"subscriptions/{self._subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Compute/virtualMachines/{vm_instance_name}/instanceView",
            )
        )

    def vm_power_off(self, resource_group_name: str, vm_instance_name: str) -> str:
        self._base_api_version = "2022-08-01"
        return self._post(
            self._build_url(
                f"subscriptions/{self._subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Compute/virtualMachines/{vm_instance_name}/powerOff",
            )
        )

    def vm_deallocate(self, resource_group_name: str, vm_instance_name: str) -> str:
        self._base_api_version = "2022-08-01"
        return self._post(
            self._build_url(
                f"subscriptions/{self._subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Compute/virtualMachines/{vm_instance_name}/deallocate",
            )
        )

    def vm_start(self, resource_group_name: str, vm_instance_name: str) -> str:
        self._base_api_version = "2022-08-01"
        return self._post(
            self._build_url(
                f"subscriptions/{self._subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Compute/virtualMachines/{vm_instance_name}/start",
            )
        )
