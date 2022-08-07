# -*- coding: utf-8 -*- #

import json
import os
import sys
from configparser import ConfigParser, NoOptionError
from pathlib import Path
from typing import Any, Iterable, Union

from google.auth.credentials import Credentials
from google.auth.exceptions import DefaultCredentialsError
from google.auth.transport.requests import AuthorizedSession
from google.cloud.compute_v1 import AggregatedListInstancesRequest, InstancesClient
from google.oauth2 import credentials, service_account
from singleton_decorator import singleton

GCP_CONFIG_PATH = f"{Path.home()}/.config/gcloud"


@singleton
class GcpSession:
    """
    GCP instance class
    """

    def __init__(self, **kwargs):
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        self._profile = self._zone = kwargs.get("profile", None)  # TODO handle profiles
        self._credentials = None
        # self._credentials, _ = default(scopes=scopes)

        try:
            creds = os.path.normpath(
                f"{GCP_CONFIG_PATH}/application_default_credentials.json"
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
            self._print_exception_text_and_exit()

        self._authed_session = AuthorizedSession(self._credentials)

        try:
            self.project_id = self._authed_session.credentials.project_id
            self.account_email = self._authed_session.credentials.service_account_email
        except AttributeError:
            try:

                config_default = ConfigParser()
                config_default.read(
                    os.path.normpath(f"{GCP_CONFIG_PATH}/configurations/config_default")
                )
                default_profile = config_default.sections()[
                    0
                ]  # TODO make profile support
                self.project_id = config_default.get(default_profile, "project")
                self.account_email = config_default.get(default_profile, "account")
            except NoOptionError:
                self._print_exception_text_and_exit()

        self._expired = self._authed_session.credentials.expired
        self._verify = self._authed_session.verify
        self._client = InstancesClient(credentials=self._credentials)
        self._zone = kwargs.get(
            "zone", os.getenv("CLOUDSDK_COMPUTE_ZONE", "europe-west2-b")
        )
        self._instances = self._get_instances()

    # ---
    @staticmethod
    def _print_exception_text_and_exit() -> str:
        print("\n------\nNo GCP Cloud platform credentials\n")
        print(
            "If service account credentials json file is available, set the environment variable\n"
            "\texport GOOGLE_APPLICATION_CREDENTIALS=/path/to/the/credentials/file\n\n",
            "To reauthenticate existent account to Google Cloud Platform\n",
            "\tgcloud auth login\n\n",
            "To authenticate a new account to Google Cloud Platform:\n",
            "\tgcloud auth login\n",
            "\tgcloud auth application-default login\n",
            "\tgcloud config set project project-name\n\n",
            "To register GCP service account credentials:\n"
            "\tgcloud auth activate-service-account --key-file=/path/to/google_application_credentials.json",
        )
        sys.exit(-1)

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
