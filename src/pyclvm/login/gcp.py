import subprocess
import sys
from plt import _get_hw
from configparser import ConfigParser, NoOptionError
from _common.user_data import get_config_path

_OS, _ = _get_hw()
_CMD = "gcloud.cmd" if _OS == "Windows" else "gcloud"

def gcp(**kwargs: str):
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
            subprocess.run(
                [
                    _CMD,
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
                _CMD,
                "auth",
                "login",
            ],
            check=True,
        )
        subprocess.run(
            [
                _CMD,
                "auth",
                "application-default",
                "login",
            ],
            check=True,
        )
        if project_id:
            subprocess.run(
                [
                    _CMD,
                    "config",
                    "set",
                    "project",
                    project_id,
                ],
                check=True,
            )
        sys.exit(0)
