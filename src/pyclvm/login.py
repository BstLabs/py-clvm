"""
help to log in on dedicated platform
"""

from pathlib import Path
import os
import sys
from typing import Union
from pyclvm.plt import plt, _get_os, _default_platform
from functools import partial
from configparser import ConfigParser, NoOptionError
import subprocess


# ---
def login(platform: str, **kwargs: str) -> Union[str, None]:
    """
    help to log in on dedicated platform
    """
    plt(platform, **kwargs)

    return {
        "AWS": partial(_login_aws, **kwargs),
        "GCP": partial(_login_gcp, **kwargs),
        "AZURE": partial(_login_azure, **kwargs),
    }[platform.upper()]()


# ---
def _login_aws(**kwargs: str) -> None:
    pass


# ---
def _login_gcp(**kwargs: str) -> None:
    config_path = _get_config_path(str(_default_platform()))
    project_id = kwargs.get("project")
    try:
        # TODO make profile support
        config_default = ConfigParser()
        config_default.read(
            os.path.normpath(f"{config_path}/configurations/config_default")
        )
        default_profile = config_default.sections()[0]
        project_id = config_default.get(default_profile, "project")
    except NoOptionError:
        if project_id:
            subprocess.run([
                "gcloud.cmd",
                "config",
                "set",
                "project",
                project_id,
            ])
        else:
            print("\n------\nSpecify project name\n\ne.g.\n\tclvm login gcp project=project-id")
            sys.exit(-1)

    except IndexError:
        subprocess.run([
            "gcloud.cmd",
            "auth",
            "login",
        ])
        subprocess.run([
            "gcloud.cmd",
            "auth",
            "application-default",
            "login",
        ])
        if project_id:
            subprocess.run([
                "gcloud.cmd",
                "config",
                "set",
                "project",
                project_id,
            ])


# ---
def _login_azure(**kwargs: str) -> None:
    pass


# ---
def _get_config_path(platform: str) -> str:
    carrier_os = _get_os()
    config_location = ""
    _path = ""

    if platform == "GCP":
        config_location = "gcloud"

    if carrier_os == "Windows":
        _path = os.path.normpath(f"{os.getenv('APPDATA')}/{config_location}")
    elif carrier_os == "Darwin":
        _path = f"{Path.home()}/.config/{config_location}"
    elif carrier_os == "Linux":
        _path = f"{Path.home()}/.config/{config_location}"
    else:
        print("Unsupported carrier operating system")
        sys.exit(-1)

    return _path



