"""
User Data Access Utility
Adopted from https://gist.github.com/jslay88/1fd8a8ba1d05ff2a4810520785a67891
"""
import sys
import pathlib
import json
from typing import Dict, Final
from jdict import jdict, set_json_decoder


_HOME: Final[pathlib.Path] = pathlib.Path.home()
_SYSTEM_USER_DIR: Final[Dict[str, str]] = dict(
    win32='AppData/Roaming',
    linux='.local/share',
    darwin='Library/Application Support'
)
_SYSTEM_CLVM_PATH: Final[pathlib.Path] = _HOME / _SYSTEM_USER_DIR[sys.platform] / 'clvm'

set_json_decoder(json)
_SYSTEM_CLVM_PATH.mkdir(parents=True, exist_ok=True)

def fetch(name: str) -> jdict:
    try:
        with (_SYSTEM_CLVM_PATH / f'{name}.json').open('r') as f:
            return json.load(f)
    except FileNotFoundError:
        return jdict()

def store(name: str, data: jdict) -> None:
    with (_SYSTEM_CLVM_PATH / f'{name}.json').open('w') as f:
        json.dump(data, f)

