import os
import boto3
from typing import Final
from datetime import datetime
from pickle import dump, load
from boto3.session import Session
from jdict import jdict, patch_module

patch_module('botocore.parsers')
patch_module('botocore.configloader')

_PATH: Final[str] = f'{os.path.expanduser("~")}/.aws/session.pkl'
_STS_CLIENT: Final = boto3.client('sts')

def _get_mfa_serial() -> str:
    config = Session()._session.get_scoped_config()
    return config.mfa_serial

def _get_credentials() -> dict:
    token_code = input('Enter MFA Code: ')
    credentials = _STS_CLIENT.get_session_token(
        SerialNumber=_get_mfa_serial(),
        TokenCode=token_code
    ).Credentials
    with open(_PATH, 'wb') as f:
        dump(credentials, f)
    return credentials


def _read_credentials():
    try:
        with open(_PATH, 'rb') as f:
            credentials = load(f)
            expiration = credentials.Expiration
            return credentials if expiration > datetime.now(expiration.tzinfo) else None
    except FileNotFoundError:
        return None
    

def _make_session(credentials) -> Session:
    return Session(
        aws_access_key_id=credentials.AccessKeyId,
        aws_secret_access_key=credentials.SecretAccessKey,
        aws_session_token=credentials.SessionToken
    )

def get_session() -> Session:
    return _make_session(_read_credentials() or _get_credentials())

