# -*- coding: utf-8 -*- #

import os
from typing import Any, Iterable, Union

from google.auth import default
from google.auth.credentials import Credentials
from google.auth.transport.requests import AuthorizedSession
from google.cloud.compute_v1 import AggregatedListInstancesRequest, InstancesClient
from singleton_decorator import singleton


@singleton
class GcpSession:
    """
    GCP instance class
    """

    def __init__(self, **kwargs):
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        self._profile = self._zone = kwargs.get("profile", None)  # TODO handle profiles
        self._credentials, _ = default(scopes=scopes)
        self._authed_session = AuthorizedSession(self._credentials)

        self.project_id = self._authed_session.credentials.project_id
        self.account_email = self._authed_session.credentials.service_account_email
        self._expired = self._authed_session.credentials.expired
        self._verify = self._authed_session.verify
        self._client = InstancesClient(credentials=self._credentials)
        self._zone = kwargs.get(
            "zone", os.getenv("CLOUDSDK_COMPUTE_ZONE", "europe-west2-b")
        )
        self._instances = self._get_instances()

    # ---
    def _get_instances(self) -> Iterable:
        request = AggregatedListInstancesRequest()
        request.project = self.project_id

        for zone, instances_in_zone in self._client.aggregated_list(request=request):
            if f"zones/{self._zone}" == zone:
                return instances_in_zone.instances

    # ---
    @property
    def instances(self) -> Iterable:
        """
        Returns Azure VM instances
        """
        return self._instances

    # ---
    def get_credentials(self) -> Credentials:
        return self._credentials

    # ---
    def get_client(self) -> InstancesClient:
        return self._client

    # ---
    def is_expired(self) -> bool:
        return self._expired

    # ---
    def is_verified(self) -> Union[bool, str, None]:
        return self._verify

    # ---
    def get_zone(self) -> Union[bool, str, None]:
        return self._zone

    # ---
    @property
    def zone(self) -> Union[Any, str, None]:
        return self._zone

    # ---
    def set_zone(self, zone: str) -> None:
        self._zone = zone

    # ---
    @property
    def project(self) -> str:
        return self.project_id


def get_session(**kwargs) -> GcpSession:
    return GcpSession(**kwargs)
