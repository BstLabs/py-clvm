from plt import _get_os
import subprocess
import os


def aws(**kwargs: str):
    """
    Install AWS cli

    Args:
        **kwargs (str): (optional) classifiers:

    Returns:
        None
    """
    {
        "Linux": _install_linux,
        "Windows": _install_windows,
        "Darwin": _install_macos,
    }[_get_os()]()


def _install_linux() -> None:
    """
    Install AWC CLI on Linux OS

    Returns:
        None
    """
    print(f"install Linux")


def _install_windows() -> None:
    """
    Install AWC CLI on Linux OS

    Returns:
        None
    """
    print(f"install Win")


def _install_macos() -> None:
    """
    Install AWC CLI on Linux OS

    Returns:
        None
    """
    print(f"install Mac")
    os.chdir(os.getenv("HOME"))
    subprocess.run(
        [
            "curl",
            "https://awscli.amazonaws.com/AWSCLIV2.pkg",
            "-o",
            "AWSCLIV2.pkg",
        ],
        check=True,
    )
    subprocess.run(
        [
            "sudo",
            "-S",
            "installer",
            "-pkg",
            "AWSCLIV2.pkg",
            "-target",
            "/",
        ],
        check=True,
    )
    os.remove("./AWSCLIV2.pkg")


# Linux or macOS
# $ export AWS_PROFILE=user1
#
# Windows
# C:\> setx AWS_PROFILE user1