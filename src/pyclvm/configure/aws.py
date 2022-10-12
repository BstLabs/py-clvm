"""
configure AWS
"""

import subprocess
import sys
from pathlib import Path
from platform import platform
from shutil import which


def _print_prerequisites() -> None:
    info = """
                            [INFO] Prerequisites...
      Please, make sure you have been provided with the required credentials.
      If you don't have it then please, contact your system administrator.

    > AWS credentials `.csv` file containing:
    - User Name
    - Access key ID
    - Secret access key

    > Role ARN

    > MFA device ARN (if activated)
    """
    print(info)


# for handling $HOME or %USERPROFILE% prefix
def _os() -> str:
    os_name = platform().split("-")[0]

    return {
        "Linux": "~/",
        "Darwin": "~/",
        "Windows": "%USERPROFILE%\\",
    }[os_name]


# main AWS CLI config command handler
def _aws_configure(*commands: str, **kwargs: str):
    try:
        assert which("aws")
    except AssertionError:
        print("[ERROR] Operation is not possible. AWS CLI is not installed")

    _profile = kwargs.get("profile", "default")
    cmd = ["aws", "configure"]
    for command in commands:
        cmd.append(command)
    cmd.append(f"--profile {_profile}")

    subprocess.run(
        " ".join(cmd),
        shell=True,
        check=True,
    )


# based on _aws_configure, imports access keys from csv file
def _add_access_keys(**kwargs: str):
    _path = Path(
        input(
            "Please, enter the access key's(.csv) relative path to $HOME(%USERPROFILE%): "
        )
    )
    try:
        _aws_configure(
            f"import --csv file://{_os()}{_path}",
            **kwargs,
        )
    except subprocess.CalledProcessError:
        print("[ERROR] File path is not correct")
        sys.exit(1)


def _set_mfa_serial(**kwargs: str):
    _mfa_serial = input("Please, enter the ARN of your MFA device: ")
    _aws_configure(
        f"set mfa_serial {_mfa_serial}",
        **kwargs,
    )


def _set_role_arn(**kwargs: str):
    _role_arn = input("Please, enter the ARN of your role: ")
    _aws_configure(
        f"set role_arn {_role_arn}",
        **kwargs,
    )


def _set_region(**kwargs: str):
    _region = kwargs.get("region", "eu-west-1")
    _aws_configure(
        f"set region {_region}",
        **kwargs,
    )
    print(f"Region set to: {_region}")


def _set_output_format(**kwargs: str):
    _format = kwargs.get("output", "json")
    _aws_configure(
        f"set output {_format}",
        **kwargs,
    )
    print(f"Output format set to: {_format}")


def _set_source_profile(**kwargs: str):
    _source_profile = kwargs.get("source_profile", "default")
    _aws_configure(
        f"set source_profile {_source_profile}",
        **kwargs,
    )
    print(f"Source profile set to: {_source_profile}")


def aws(**kwargs: str):
    """
    configure AWS

    Args:
        **kwargs (str): (optional) classifiers: profile, output, region, source_profile

    Returns:
        None
    """
    _print_prerequisites()
    try:
        _add_access_keys(**kwargs)
        _set_mfa_serial(**kwargs)
        _set_role_arn(**kwargs)
        _set_region(**kwargs)
        _set_output_format(**kwargs)
        _set_source_profile(**kwargs)
    except KeyboardInterrupt:
        print("\n\n[INFO] Terminated with keyboard interrupt...")
