from subprocess import STDOUT, TimeoutExpired, check_output
import sys
import os
from plt import _get_hw
import json
from _common.user_data import get_config_path

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import DefaultAzureCredential


_OS, _ = _get_hw()
_CMD = "az.cmd" if _OS == "Windows" else "az"


def azure(**kwargs: str):
    """
    Login to Azure console

    Args:
        **kwargs (str): (optional) classifiers:

    Returns:
        None
    """
    def _login():
        try:
            check_output(
                [
                    _CMD,
                    "login",
                ],
                stderr=STDOUT,
                timeout=30,
            )
        except TimeoutExpired as er:
            print(f"\n---\n{er}\n---\n")
            sys.exit(-1)
        sys.exit(0)

    config_path = get_config_path()
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
