"""clear stored session credentials."""

import os

from pyclvm._common.session_aws import make_file_name
from pyclvm._common.user_data import get_credentials_file_path


def clear(**kwargs: str) -> None:
    """
    clear stored session credentials.

    Args:
        **kwargs (str): Provide profile name

    Returns:
        None
    """

    profile_name = kwargs.get("profile", "default")
    credentials_file = make_file_name(profile_name)
    credentials_file_path = get_credentials_file_path(credentials_file)
    try:
        os.remove(credentials_file_path)
        print("[INFO] Successfully removed stored credentials")
    except FileNotFoundError:
        print("[SKIPPED] as there is no such file or directory to be removed...")
