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
from typing import Tuple, Union

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import DefaultAzureCredential
from azure.mgmt.subscription import SubscriptionClient

from pyclvm.plt import _default_platform, _get_os, plt

_OS = _get_os()


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
            subprocess.run(
                [
                    "gcloud.cmd" if _OS == "Windows" else "gcloud",
                    "config",
                    "set",
                    "project",
                    project_id,
                ]
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
            ]
        )
        subprocess.run(
            [
                "gcloud.cmd" if _OS == "Windows" else "gcloud",
                "auth",
                "application-default",
                "login",
            ]
        )
        if project_id:
            subprocess.run(
                [
                    "gcloud.cmd" if _OS == "Windows" else "gcloud",
                    "config",
                    "set",
                    "project",
                    project_id,
                ]
            )
        sys.exit(0)


# ---
def _login_azure(**kwargs: str) -> Union[None, Tuple]:
    def _login():
        subprocess.run(
            [
                "az.cmd" if _OS == "Windows" else "az",
                "login",
            ]
        )
        sys.exit(0)

    config_path = _get_config_path(str(_default_platform()))
    if not os.path.isdir(config_path):
        _login()

    with open(os.path.normpath(f"{config_path}/azureProfile.json"), "rb") as cfg:
        azure_cfg = json.load(cfg)

    subscription_id = ""

    try:
        for subscription in azure_cfg["subscriptions"]:
            if subscription["isDefault"]:
                subscription_id = subscription["id"]

        default_credentials = DefaultAzureCredential()
        subscription_client = SubscriptionClient(default_credentials)

        for subscription in subscription_client.subscriptions.list():
            if subscription.subscription_id == subscription_id:
                return (
                    default_credentials,
                    subscription.display_name,
                    subscription.subscription_id,
                )
        raise ClientAuthenticationError()
    except (ClientAuthenticationError, KeyError):
        _login()


# ---
def _get_config_path(platform: str) -> str:
    # carrier_os = _get_os()
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