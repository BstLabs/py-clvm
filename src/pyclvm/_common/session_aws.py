import getpass
import os
import platform
import sys
from datetime import datetime
from typing import Dict, Final, Optional

import backoff
import boto3
import botocore
from boto3.session import Session
from jdict import jdict, patch_module

from pyclvm.login import _login_aws

from .user_data import fetch, store

patch_module("botocore.parsers")
patch_module("botocore.configloader")


_STS_CLIENT: Final = boto3.client("sts")


class Credentials(jdict):
    AccessKeyId: str
    SecretAccessKey: str
    SessionToken: str
    Expiration: str
    Region: str


def make_file_name(profile: str) -> str:
    return f"aws-{profile}-credentials"


def _read_credentials(profile: str) -> Optional[Credentials]:
    try:
        credentials = fetch(make_file_name(profile))
        expiration = datetime.fromisoformat(credentials.Expiration)
        return credentials if expiration > datetime.now(expiration.tzinfo) else None
    except FileNotFoundError:
        return None


def _get_config(profile: str) -> jdict:
    return Session(profile_name=profile)._session.get_scoped_config()


def _get_mfa_serial(profile: str) -> str:
    """
    Gets MFA serial ARN via client STS request
    """
    sts = jdict(Session(profile_name=profile).client("sts").get_caller_identity())
    return sts.Arn.replace("user", "mfa", 1)


def _store_credentials(profile: str, credentials: Credentials) -> None:
    credentials.Expiration = datetime.isoformat(
        credentials.Expiration
    )  # to make it json serializable
    store(make_file_name(profile), credentials)


def _invalid_mfa_code_provided(details):
    print(
        "\n > Invalid MFA code provided or other authentication problem, please try again!\n"
    )


def _give_up(e):
    print("\n > Giving up after multiple fails...")
    _login_aws()


@backoff.on_exception(
    backoff.expo,
    botocore.exceptions.ClientError,
    max_tries=3,
    on_giveup=_give_up,
    on_backoff=_invalid_mfa_code_provided,
)
@backoff.on_exception(
    backoff.expo,
    botocore.exceptions.ParamValidationError,
    max_tries=3,
    on_giveup=_give_up,
    on_backoff=_invalid_mfa_code_provided,
)
def _get_profile_credentials(profile: str, config: jdict) -> Credentials:
    # That means the clvm vscode start was called no need to ask twice for token
    if os.getenv("VSCODE_AWS_PROMPT"):
        sys.exit(0)

    token_code = getpass.getpass("Enter MFA Code: ")

    credentials = (
        Session(
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            profile_name=profile,
            region_name=config.region,
        )
        .client("sts")
        .get_session_token(SerialNumber=_get_mfa_serial(profile), TokenCode=token_code)
        .Credentials
    )

    credentials.Region = config.region
    _store_credentials(profile, credentials)
    return credentials


def _get_role_credentials(profile: str, config: jdict) -> Credentials:
    source_profile = config.source_profile
    source_config = _get_config(source_profile)
    source_credentials = _read_credentials(source_profile) or _get_profile_credentials(
        source_profile, source_config
    )
    credentials = (
        _make_session(source_credentials, profile)
        .client("sts")
        .assume_role(
            RoleArn=config.role_arn,
            RoleSessionName=f"{getpass.getuser()}@{platform.node()}-session",
        )
        .Credentials
    )
    credentials.Region = source_config.region
    _store_credentials(profile, credentials)
    return credentials


def _get_credentials(profile: str) -> Dict:
    config = _get_config(profile)
    return (
        _get_role_credentials(profile, config)
        if "role_arn" in config
        else _get_profile_credentials(profile, config)
    )


def _make_session(credentials, profile) -> Session:
    return Session(
        aws_access_key_id=credentials.AccessKeyId,
        aws_secret_access_key=credentials.SecretAccessKey,
        aws_session_token=credentials.SessionToken,
        region_name=credentials.Region,
        profile_name=profile,
    )


def get_session(kwargs: Dict[str, str]) -> Session:
    profile = kwargs.get("profile", "default")
    boto3.setup_default_session(profile_name=profile)
    return _make_session(
        (_read_credentials(profile) or _get_credentials(profile)), profile
    )
