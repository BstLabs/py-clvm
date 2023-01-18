from plt import _get_os
import subprocess
import os
import requests
from zipfile import ZipFile
from uuid import uuid4
import shutil


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
    print(f"Install AWS CLI on Linux")
    tmp_dir = f"{os.getenv('HOME')}/{uuid4()}"
    os.mkdir(tmp_dir, 0o0700)
    target_file = "awscli-exe-linux-x86_64.zip"
    cli_file = requests.get(f"https://awscli.amazonaws.com/{target_file}")
    tmp_file = f"{tmp_dir}/{target_file}"
    open(tmp_file, "wb").write(cli_file.content)
    with ZipFile(tmp_file, "r") as z:
        z.extractall(path=tmp_dir)
    subprocess.run(
        [
            "sudo",
            "sh",
            f"{tmp_dir}/aws/install",
            "--update",
        ],
        check=True,
    )
    shutil.rmtree(tmp_dir, ignore_errors=False, onerror=None)


def _install_windows() -> None:
    """
    Install AWC CLI on Linux OS

    Returns:
        None
    """
    subprocess.run(
        [
            "msiexec.exe",
            "/i",
            "https://awscli.amazonaws.com/AWSCLIV2.msi",
        ],
        check=True,
    )


def _install_macos() -> None:
    """
    Install AWC CLI on Linux OS

    Returns:
        None
    """
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