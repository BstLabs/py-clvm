"""
help to log in on dedicated platform
"""
import json
import os
import subprocess
import sys
from configparser import ConfigParser, NoOptionError
from functools import partial
from pathlib import Path
from subprocess import STDOUT, TimeoutExpired, check_output
from typing import Tuple, Union

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import DefaultAzureCredential

from pyclvm.plt import _default_platform, _get_os, plt

_OS = _get_os()


# ---
def login(platform: str, **kwargs: str) -> Union[str, None]:
    """
    help to log in on dedicated platform

    Args:
        platform (str): cloud platform name (AWS, GCP, AZURE)
        **kwargs (str): (optional) additional arguments, currently only `project`

    Returns:
        Union[str, None]
    """
    platform = platform.split("=")[-1]
    try:
        plt(platform, **kwargs)
    except TypeError:  # TODO exception occurs in dynacli, try to pass the exception trace here
        print(
            "\n------\nMultiple platform references. User the only one."
            "\ne.g.\n\tclvm login azure\n\tclvm login platform=azure"
        )

    return {
        "AWS": partial(_login_aws, **kwargs),
        "GCP": partial(_login_gcp, **kwargs),
        "AZURE": partial(_login_azure, **kwargs),
    }[platform.upper()]()


# ---
def _login_aws(**kwargs: str) -> None:
    profile_name = kwargs.get("profile", "default")
    print(
        f'\n------\nPlease, fix your AWS credentials and back again. Profile name "{profile_name}"\n'
    )
    subprocess.run(
        [
            "aws.exe" if _OS == "Windows" else "aws",
            "configure",
            f"--profile={profile_name}",
        ],
        check=True,
    )
    sys.exit(0)


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
            subprocess.run(
                [
                    "gcloud.cmd" if _OS == "Windows" else "gcloud",
                    "config",
                    "set",
                    "project",
                    project_id,
                ],
                check=True,
            )
        else:
            print(
                "\n------\nSpecify project name\n\ne.g.\n\tclvm login gcp project=project-id"
            )
            sys.exit(-1)

    except IndexError:
        subprocess.run(
            [
                "gcloud.cmd" if _OS == "Windows" else "gcloud",
                "auth",
                "login",
            ],
            check=True,
        )
        subprocess.run(
            [
                "gcloud.cmd" if _OS == "Windows" else "gcloud",
                "auth",
                "application-default",
                "login",
            ],
            check=True,
        )
        if project_id:
            subprocess.run(
                [
                    "gcloud.cmd" if _OS == "Windows" else "gcloud",
                    "config",
                    "set",
                    "project",
                    project_id,
                ],
                check=True,
            )
        sys.exit(0)


# ---
def _login_azure(**kwargs: str) -> Union[None, Tuple]:
    def _login():
        try:
            check_output(
                [
                    "az.cmd" if _OS == "Windows" else "az",
                    "login",
                ],
                stderr=STDOUT,
                timeout=30,
            )
        except TimeoutExpired as er:
            print(f"\n---\n{er}\n---\n")
            sys.exit(-1)
        sys.exit(0)

    config_path = _get_config_path(str(_default_platform()))
    if not os.path.isdir(config_path):
        _login()

    if kwargs.get("expired", False):
        _login()

    with open(os.path.normpath(f"{config_path}/azureProfile.json"), "rb") as cfg:
        azure_cfg = json.load(cfg)

    try:
        credentials_params = {
            "exclude_shared_token_cache_credential": True,
        }
        default_credentials = DefaultAzureCredential(**credentials_params)
        for subscription in azure_cfg["subscriptions"]:
            if subscription["isDefault"]:
                return (
                    default_credentials,
                    subscription["name"],
                    subscription["id"],
                    # subscription["tenantId"],
                    # subscription.get("user", None),
                )
        raise ClientAuthenticationError()
    except (ClientAuthenticationError, KeyError):
        _login()


# ---
def _get_config_path(platform: str) -> str:
    _path = ""

    if platform == "GCP":
        config_location = "gcloud"

        if _OS == "Windows":
            _path = os.path.normpath(f"{os.getenv('APPDATA')}/{config_location}")
        elif _OS == "Darwin":
            _path = f"{Path.home()}/.config/{config_location}"
        elif _OS == "Linux":
            _path = f"{Path.home()}/.config/{config_location}"
        else:
            print("Unsupported carrier operating system")
            sys.exit(-1)

    elif platform == "AZURE":
        config_location = ".azure"

        if _OS == "Windows":
            _path = os.path.normpath(f"{os.getenv('USERPROFILE')}/{config_location}")
        elif _OS == "Darwin":
            _path = f"{Path.home()}/{config_location}"
        elif _OS == "Linux":
            _path = f"{Path.home()}/{config_location}"
        else:
            print("Unsupported carrier operating system")
            sys.exit(-1)

    return _path
