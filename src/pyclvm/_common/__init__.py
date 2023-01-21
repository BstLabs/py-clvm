"""
Common clvm utilities
"""

import os
from plt import _get_hw, _default_platform
from pathlib import Path

_OS, _ = _get_hw()
_PROFILE_PATH = Path.home()

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
