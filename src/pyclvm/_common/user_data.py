"""
User Data Access Utility
Adopted from https://gist.github.com/jslay88/1fd8a8ba1d05ff2a4810520785a67891
"""
import json
import os
import pathlib
from typing import Final

from jdict import jdict, set_json_decoder

_SYSTEM_CLVM_PATH: Final[pathlib.Path] = os.path.expanduser("~/.clvm")
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
