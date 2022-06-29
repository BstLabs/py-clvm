# -*- coding: utf-8 -*- #

import os
from typing import Any, Union, Tuple, Iterable, Dict

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.subscription import SubscriptionClient

from singleton_decorator import singleton

from collections import defaultdict

# import sqlite3


@singleton
class AzureSession:
    """
    Azure session class
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
        # self._conn = self._init_db()
        self._instances = self._get_instances()

    # ---
    def _get_instances(self) -> Dict:
        instances = defaultdict()
        for instance in self._client.virtual_machines.list_all():
            resource_group = instance.id.split("/")[4]
            location = instance.location
            instances[f"{instance.name}"] = {
                "instance_id": instance.vm_id,
                "resource_group": resource_group,
                "location": location,
                "instance_name": instance.name,
            }
        return dict(instances)

    # ---
    @property
    def instances(self) -> Dict:
        """
        Returns Azure VM instances
        """
        return self._instances


    # @staticmethod
    # # ---
    # def _init_db() -> sqlite3.Connection:
    #     db_path = os.path.normpath(f"{os.getenv('HOME')}/.clvm")
    #     os.makedirs(name=db_path, mode=0o700, exist_ok=True)
    #     db_file = f"{db_path}/cache.azure.db"
    #     if os.path.isfile(db_file):
    #         return sqlite3.connect(db_file)
    #     else:
    #         conn = sqlite3.connect(db_file)
    #         cur = conn.cursor()
    #         cur.execute("PRAGMA foreign_keys=ON")
    #         conn.commit()
    #         cur.execute("""
    #             CREATE TABLE timestamps (
    #                 uid INTEGER PRIMARY KEY AUTOINCREMENT,
    #                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    #                 note CHAR(64)
    #             )
    #         """)
    #         conn.commit()
    #         cur.execute("""
    #             CREATE TABLE instances (
    #                 uid INTEGER PRIMARY KEY AUTOINCREMENT,
    #                 timestamp INTEGER,
    #                 id CHAR(64),
    #                 name CHAR(256),
    #                 storage_group CHAR(128),
    #                 location CHAR(32),
    #                 FOREIGN KEY(timestamp) REFERENCES timestamps(uid)
    #             )
    #         """)
    #         conn.commit()
    #         return conn
    #
    # # ---
    # @property
    # def conn(self) :
    #     return self._conn
    #
    # # ---
    # def __del__(self):
    #     self._conn.close()

    # ---
    def _get_subscription(self) -> Tuple[str, str]:
        subscription_client = SubscriptionClient(self._credentials)
        for r in subscription_client.subscriptions.list():
            if r.display_name:
                return r.display_name, r.subscription_id

    # ---
    @property
    def subscription(self) -> Any:
        """
        Returns Azure Subscription name
        """
        return self._subscription_id

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

    # ---
    def get_resource_group(self) -> Union[bool, str, None]:
        return self._resource_group

    # ---
    @property
    def resource_group(self) -> Union[Any, str, None]:
        return self._resource_group

    # ---
    def set_resource_group(self, resource_group: str) -> None:
        self._resource_group = resource_group


def get_session(**kwargs) -> AzureSession:
    return AzureSession(**kwargs)
