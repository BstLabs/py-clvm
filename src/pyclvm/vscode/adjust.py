import os

import commentjson


def adjust() -> None:
    """
    adjust vscode global settings.
    currently only supported on Linux.

    Args:
        None

    Returns:
        None
    """

    path_ = os.path.expanduser("~/.config/Code/User/settings.json")

    with open(path_, "r") as jsondata:
        settings = commentjson.loads(jsondata.read())
        settings["remote.SSH.showLoginTerminal"] = True
        settings["remote.SSH.useLocalServer"] = False
        settings["remote.SSH.connectTimeout"] = 120

    with open(path_, "w") as jsondata:
        commentjson.dump(settings, jsondata, indent=6)

    print("VSCode settings updated for clvm usage...")
