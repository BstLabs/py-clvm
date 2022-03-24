import os
import boto3
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

def _make_file_name(profile: str) -> str:
    return f'aws-{profile}-credentials'

def _get_mfa_serial(profile: str) -> str:
    config = Session(profile_name=profile)._session.get_scoped_config()
    return config.mfa_serial

def _get_credentials(profile: str) -> dict:
    token_code = input('Enter MFA Code: ')
    credentials = _STS_CLIENT.get_session_token(
        SerialNumber=_get_mfa_serial(profile),
        TokenCode=token_code
    ).Credentials
    credentials.Expiration=datetime.isoformat(credentials.Expiration) # to make it json serializable
    store(_make_file_name(profile), credentials)
    return credentials

def _read_credentials(profile: str) -> Credentials:
    try:
        credentials = fetch(_make_file_name(profile))
        expiration = datetime.fromisoformat(credentials.Expiration)
        return credentials if expiration > datetime.now(expiration.tzinfo) else None
    except FileNotFoundError:
        return None
    

def _make_session(credentials) -> Session:
    return Session(
        aws_access_key_id=credentials.AccessKeyId,
        aws_secret_access_key=credentials.SecretAccessKey,
        aws_session_token=credentials.SessionToken
    )

def get_session(kwargs: Dict[str, str]) -> Session:
    profile = kwargs.get('profile', 'default')
    return _make_session(_read_credentials(profile) or _get_credentials(profile))

