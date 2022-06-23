# -*- coding: utf-8 -*- #

from typing import Optional

from google.auth import default
from google.auth.credentials import Credentials
from google.auth.transport.requests import AuthorizedSession


class GcpSession:
    """
    GCP instance class
    """

    def __init__(self, profile: Optional[str] = None):
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        self._profile = profile  # TODO handle profiles
        self._credentials, _ = default(scopes=scopes)
        self._authed_session = AuthorizedSession(self._credentials)

        self.project_id = self._authed_session.credentials.project_id
        self.account_email = self._authed_session.credentials.service_account_email
        self._expired = self._authed_session.credentials.expired
        self._verify = self._authed_session.verify

    # ---
    def get_credentials(self) -> Credentials:
        return self._credentials

    # ---
    def is_expired(self) -> bool:
        return self._expired

    # ---
    def is_verified(self) -> bool:
        return self._verify


def get_session(**kwargs) -> GcpSession:
    profile = kwargs.get("profile", None)
    return GcpSession(profile=profile)
