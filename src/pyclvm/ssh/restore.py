# -*- coding: utf-8 -*- #

import os
from os.path import expanduser, join
from shutil import copyfile
from typing import Final

_SSH_DIR: Final[str] = expanduser(join("~", ".ssh"))
_SSH_CONFIG: Final[str] = join(_SSH_DIR, "config")
_BACKUP_SUFFIX = "ORIG"


# ---
def restore() -> None:
    """
    restore previous SSH configuration file
    """
    try:
        backup_file = f"{_SSH_CONFIG}.{_BACKUP_SUFFIX}"
        copyfile(backup_file, _SSH_CONFIG)
        os.chmod(_SSH_CONFIG, 0o600)
        os.remove(backup_file)
    except FileNotFoundError as err:
        print("-" * 50, f"Exception: {err}", sep="\n\n", end="\n")
