import os
import shutil
import subprocess
import sys
from platform import uname
from uuid import uuid4
from zipfile import ZipFile

import requests
from plt import _get_os


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
    print("\n---\nInstall AWS CLI on Linux\n")
    tmp_dir = f"{os.getenv('HOME')}/{uuid4()}"
    os.mkdir(path=tmp_dir, mode=0o0700)
    target_file = f"awscli-exe-linux-{uname().machine}.zip"
    cli_file = requests.get(f"https://awscli.amazonaws.com/{target_file}")
    tmp_file = f"{tmp_dir}/{target_file}"
    open(tmp_file, "wb").write(cli_file.content)
    with ZipFile(tmp_file, "r") as z:
        z.extractall(path=tmp_dir)
    os.chmod(path=f"{tmp_dir}/aws/dist/aws", mode=0o755)
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
    Install AWC CLI on Windows OS

    Returns:
        None
    """
    print("\n---\nInstall AWS CLI on Windows\n")
    try:
        subprocess.run(
            [
                "msiexec.exe",
                "/i",
                "https://awscli.amazonaws.com/AWSCLIV2.msi",
            ],
            check=True,
        )
    except subprocess.CalledProcessError:
        sys.exit(-1)


def _install_macos() -> None:
    """
    Install AWC CLI on macOS

    Returns:
        None
    """
    print("\n---\nInstall AWS CLI on macOS\n")
    tmp_dir = f"{os.getenv('HOME')}/{uuid4()}"
    os.mkdir(path=tmp_dir, mode=0o0700)
    target_file = "AWSCLIV2.pkg"
    cli_file = requests.get(f"https://awscli.amazonaws.com/{target_file}")
    tmp_file = f"{tmp_dir}/{target_file}"
    open(tmp_file, "wb").write(cli_file.content)
    subprocess.run(
        [
            "sudo",
            "-S",
            "installer",
            "-pkg",
            tmp_file,
            "-target",
            "/",
        ],
        check=True,
    )
    shutil.rmtree(tmp_dir, ignore_errors=False, onerror=None)
