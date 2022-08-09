import os
from pathlib import Path

import commentjson
from pyclvm.plt import _get_os


def adjust() -> None:
    """
    adjust vscode global settings.
    currently only supported on Linux.

    Args:
        None

    Returns:
        None
    """

    config_location = "Code/User/settings.json"

    if _get_os() == "Windows":
        path_ = os.path.normpath(f"{os.getenv('APPDATA')}/{config_location}")
    else:
        path_ = f"{Path.home()}/.config/{config_location}"

    with open(path_, "rb") as cfg:
        settings = commentjson.loads(cfg.read())
        settings["remote.SSH.showLoginTerminal"] = True
        settings["remote.SSH.useLocalServer"] = False
        settings["remote.SSH.connectTimeout"] = 120

    with open(path_, "w") as cfg:
        commentjson.dump(settings, cfg, indent=4)

    print("VSCode settings updated for clvm usage...")
