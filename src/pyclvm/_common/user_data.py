"""
User Data Access Utility
Adopted from https://gist.github.com/jslay88/1fd8a8ba1d05ff2a4810520785a67891
"""
import json
import pathlib
import sys
from typing import Dict, Final

from jdict import jdict, set_json_decoder

_HOME: Final[pathlib.Path] = pathlib.Path.home()

_SYSTEM_USER_DIR: Final[Dict[str, str]] = {
    "win32": "AppData/Roaming",
    "linux": ".local/share",
    "darwin": "Library/Application Support",
}

_SYSTEM_CLVM_PATH: Final[pathlib.Path] = _HOME / _SYSTEM_USER_DIR[sys.platform] / "clvm"

set_json_decoder(json)

_SYSTEM_CLVM_PATH.mkdir(parents=True, exist_ok=True)


def _get_path(name: str) -> pathlib.Path:
    return _SYSTEM_CLVM_PATH / f"{name}.json"


def fetch(name: str) -> jdict:
    with _get_path(name).open("r") as file:
        return json.load(file)


def store(name: str, data: jdict) -> None:
    with _get_path(name).open("w") as file:
        json.dump(data, file)


def remove(name: str) -> None:
    _get_path(name).unlink(missing_ok=True)
