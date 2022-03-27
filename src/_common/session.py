import os
import boto3
import getpass
import platform
from typing import Final, Dict
from datetime import datetime
from boto3.session import Session
from jdict import jdict, patch_module
from .user_data import fetch, store


patch_module('botocore.parsers')
patch_module('botocore.configloader')


_STS_CLIENT: Final = boto3.client('sts')


class Credentials(jdict):
    AccessKeyId: str
    SecretAccessKey: str
    SessionToken: str
    Expiration: str
    Region: str


def _make_file_name(profile: str) -> str:
    return f'aws-{profile}-credentials'


def _read_credentials(profile: str) -> Credentials:
    try:
        credentials = fetch(_make_file_name(profile))
        expiration = datetime.fromisoformat(credentials.Expiration)
        return credentials if expiration > datetime.now(expiration.tzinfo) else None
    except FileNotFoundError:
        return None
    

def _get_config(profile: str) -> jdict:
    return Session(profile_name=profile)._session.get_scoped_config()
 

def _get_mfa_serial(config: jdict) -> str:
    return config.mfa_serial


def _store_credentials(profile: str, credentials: Credentials) -> None:
    credentials.Expiration=datetime.isoformat(credentials.Expiration) # to make it json serializable
    store(_make_file_name(profile), credentials)
    

def _get_profile_credentials(profile: str) -> Credentials:
    config = _get_config(profile)
    token_code = input('Enter MFA Code: ')
    credentials = _STS_CLIENT.get_session_token(
        SerialNumber=_get_mfa_serial(config),
        TokenCode=token_code
    ).Credentials
    credentials.Region = config.Region
    _store_credentials(profile, credentials)
    return credentials


def _make_session(credentials) -> Session:
    return Session(
        aws_access_key_id=credentials.AccessKeyId,
        aws_secret_access_key=credentials.SecretAccessKey,
        aws_session_token=credentials.SessionToken,
        region_name=credentials.Region
    )


def _get_role_credentials(profile: str, config: jdict):
    source_credentials = _read_credentials(config.source_profile) or _get_profile_credentials(config.source_profile)
    credentials = _make_session(source_credentials).client('sts').assume_role(
        RoleArn=config.role_arn,
        RoleSessionName=f'{getpass.getuser()}@{platform.node()}-session'
    ).Credentials
    credentials.Region = config.Region
    _store_credentials(profile, credentials)
    return credentials


def _get_credentials(profile: str) -> dict:
    config = _get_config(profile)
    return _get_role_credentials(profile, config) if 'role_arn' in config else _get_profile_credentials(config)


def get_session(kwargs: Dict[str, str]) -> Session:
    profile = kwargs.get('profile', 'default')
    return _make_session(_read_credentials(profile) or _get_credentials(profile))

