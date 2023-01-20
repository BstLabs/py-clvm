"""
User Data Access Utility
Adopted from https://gist.github.com/jslay88/1fd8a8ba1d05ff2a4810520785a67891
"""
import json
import os
import pathlib
from typing import Final
from pathlib import Path

from jdict import jdict, set_json_decoder

from plt import _get_hw, _default_platform

_OS, _ = _get_hw()
_PROFILE_PATH = Path.home()

if _OS == "Windows":
    _PROFILE_PATH = os.path.normpath(os.getenv('USERPROFILE'))


_SYSTEM_CLVM_PATH: Final[str] = f"{_PROFILE_PATH}/.clvm"
SYSTEM_CLVM_PATH = pathlib.Path(_SYSTEM_CLVM_PATH)

set_json_decoder(json)

SYSTEM_CLVM_PATH.mkdir(parents=True, exist_ok=True)



def get_credentials_file_path(name: str) -> pathlib.Path:
    return SYSTEM_CLVM_PATH / f"{name}.json"


def fetch(name: str) -> jdict:
    with get_credentials_file_path(name).open("r") as file:
        return json.load(file)


def store(name: str, data: jdict) -> None:
    with get_credentials_file_path(name).open("w") as file:
        json.dump(data, file)


def remove(name: str) -> None:
    get_credentials_file_path(name).unlink(missing_ok=True)


def get_config_path() -> str:
    def _gcp_config_path():
        if _OS == "Windows":
            return os.path.normpath(f"{os.getenv('APPDATA')}/gcloud")
        return f"{_PROFILE_PATH}/.config/gcloud"

    return {
        "AWS": f"{_PROFILE_PATH}/.aws",
        "GCP": _gcp_config_path(),
        "AZURE": f"{_PROFILE_PATH}/.azure",
    }[_default_platform().upper()]

    # return _path
