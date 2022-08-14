# -*- coding: utf-8 -*- #

import json
import os
import subprocess
import sys
from configparser import ConfigParser, NoOptionError
from typing import Any, Iterable, Union

from google.auth.credentials import Credentials
from google.auth.exceptions import DefaultCredentialsError, RefreshError
from google.auth.transport.requests import AuthorizedSession
from google.cloud.compute_v1 import AggregatedListInstancesRequest, InstancesClient
from google.oauth2 import credentials, service_account
from singleton_decorator import singleton

from pyclvm.login import _get_config_path, _login_gcp
from pyclvm.plt import _get_os

_OS = _get_os()


@singleton
class GcpSession:
    """
    GCP instance class
    """

    def __init__(self, **kwargs):
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        self._profile = self._zone = kwargs.get("profile", None)  # TODO handle profiles
        self._credentials = None

        try:
            creds = os.path.normpath(
                f"{_get_config_path('GCP')}/application_default_credentials.json"
            )
            with open(creds, "rb") as src:
                info = json.load(src)
            self._credentials = credentials.Credentials.from_authorized_user_info(
                info, scopes=scopes
            )

        except (DefaultCredentialsError, FileNotFoundError):
            creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if creds:
                with open(creds, "rb") as src:
                    info = json.load(src)
                self._credentials = (
                    service_account.Credentials.from_service_account_info(
                        info, scopes=scopes
                    )
                )

        if not self._credentials:
            _login_gcp(**kwargs)

        self._authed_session = AuthorizedSession(self._credentials)

        try:
            self.project_id = self._authed_session.credentials.project_id
            self.account_email = self._authed_session.credentials.service_account_email
        except AttributeError:
            try:
                #
                # TODO make profile support
                config_default = ConfigParser()
                config_default.read(
                    os.path.normpath(
                        f"{_get_config_path('GCP')}/configurations/config_default"
                    )
                )
                default_profile = config_default.sections()[0]
                self.project_id = config_default.get(default_profile, "project")
                self.account_email = config_default.get(default_profile, "account")
            except NoOptionError:
                print(
                    "\n------\nSpecify project name\n\ne.g.\n\tclvm login gcp project=project-id"
                )
                sys.exit(-1)

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


# ---
def get_session(**kwargs) -> GcpSession:
    try:
        return GcpSession(**kwargs)
    except RefreshError:
        subprocess.run(
            [
                "gcloud.cmd" if _OS == "Windows" else "gcloud",
                "auth",
                "login",
                "--update-adc",
            ]
        )
        return GcpSession(**kwargs)
