import subprocess
from subprocess import STDOUT, TimeoutExpired, check_output
import sys
from plt import _get_hw
from configparser import ConfigParser, NoOptionError
from _common import get_config_path

_OS, _ = _get_hw()
_CMD = "gcloud.cmd" if _OS == "Windows" else "gcloud"


def _spawn(cmd: list, timeout: int = 30) -> None:
    """
    Runs a subprocess with timeout

    Args:
        cmd (list): a command with arguments in a list
        timeout (int): (optional) timeout duration

    Returns:
        None
    """
    try:
        check_output(
            cmd,
            stderr=STDOUT,
            timeout=timeout,
        )
    except TimeoutExpired as er:
        print(f"\n---\n{er}\n---\n")
        sys.exit(-1)


def gcp(**kwargs: str) -> None:
    """
    Login to GCP console

    Args:
        **kwargs (str): (optional) classifiers:

    Returns:
        None
    """
    project_id = kwargs.get("project")
    try:
        # TODO make profile support
        config_default = ConfigParser()
        config_default.read(f"{get_config_path()}/configurations/config_default")
        default_profile = config_default.sections()[0]
        project_id = config_default.get(default_profile, "project")
    except NoOptionError:
        if project_id:
            _spawn(
                [
                    _CMD,
                    "config",
                    "set",
                    "project",
                    project_id,
                ],
            )
        else:
            print(
                "\n------\nSpecify project name\n\ne.g.\n\tclvm login gcp project=project-id"
            )
            sys.exit(-1)

    except IndexError:
        _spawn(
            [
                _CMD,
                "auth",
                "login",
            ],
        )
        _spawn(
            [
                _CMD,
                "auth",
                "application-default",
                "login",
            ],
        )
        if project_id:
            _spawn(
                [
                    _CMD,
                    "config",
                    "set",
                    "project",
                    project_id,
                ],
            )
        sys.exit(0)
