import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import List

# TODO: form it at install time- no reason to detect platform dynamically
# TODO: provide support for Mac, Windows, CentOS


def _run_script(*commands: List[str]) -> None:
    # TODO: generic open source?
    for command in commands:
        try:
            print(" ".join(command))
            subprocess.run(command, check=True, shell=True)
        except subprocess.CalledProcessError as e:
            print(e.output)
            sys.exit(1)


def install() -> None:
    """
    install vscode local

    Args:
        None

    Returns:
        None

    """
    env = platform.uname()
    if env.system == "Linux":
        # assert "Linux" == env.system
        assert "Ubuntu" in env.version
        assert "x86_64" == env.machine
        _run_script(
            ["sudo", "apt", "update"],
            [
                "sudo",
                "apt",
                "install",
                "-y",
                "software-properties-common",
                "apt-transport-https",
                "wget",
            ],
            [
                "wget",
                "-q",
                "https://packages.microsoft.com/keys/microsoft.asc",
                "-O",
                "/tmp/microsoft.asc",
            ],
            ["sudo", "apt-key", "add", "/tmp/microsoft.asc"],
            [
                "sudo",
                "add-apt-repository",
                "deb [arch=amd64] https://packages.microsoft.com/repos/vscode stable main",
            ],
            ["sudo", "apt", "install", "-y", "code"],
            ["code", "--install-extension", "ms-vscode.makefile-tools"],
            ["code", "--install-extension", "ms-python.python"],
            ["code", "--install-extension", "ms-vscode-remote.remote-ssh"],
            ["code", "--install-extension", "valentjn.vscode-ltex"],
        )
    # --- MacOS install script wia brew ---
    elif env.system == "Darwin":

        home = os.path.expanduser("~")
        bash_profile = f"{home}/.bash_profile"
        brew_path = "/opt/homebrew/bin/brew"
        vscode_path = "/opt/homebrew/bin/code"
        pyqt_path = "/opt/homebrew/opt/pyqt5/lib/python3.9/site-packages"

        if not Path(brew_path).is_file():
            _run_script(
                [
                    "/bin/bash",
                    "-c",
                    '"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
                ]
            )

        if Path(vscode_path).is_file():
            _run_script(
                ["brew", "install", "visual-studio-code"],
                ["brew", "install", "qt5", "pyqt5"],
            )

            export_line = f"export PYTHONPATH=$PYTHONPATH:{pyqt_path}\n"
            flag = False

            with open(bash_profile, "r+", encoding="utf8") as file:
                for line in file.readlines():
                    if line == export_line:
                        flag = True
                        break

            if not flag:
                with open(bash_profile, "a", encoding="utf8") as file:
                    file.write(export_line)

            sys.path.append(pyqt_path)

            _run_script(
                ["code", "--install-extension", "ms-vscode.makefile-tools"],
                ["code", "--install-extension", "ms-python.python"],
                ["code", "--install-extension", "ms-vscode-remote.remote-ssh"],
                ["code", "--install-extension", "valentjn.vscode-ltex"],
            )
    elif env.system == "Windows":
        code = os.path.join(
            os.path.expanduser("~"),
            "AppData\\Local\\Programs\\Microsoft VS Code\\bin\\code",
        )
        _run_script(
            ["winget", "install", "vscode"],  # Windows 10+ compatible package manager
            [code, "--install-extension", "ms-vscode.makefile-tools"],
            [code, "--install-extension", "ms-python.python"],
            [code, "--install-extension", "ms-vscode-remote.remote-ssh"],
            [code, "--install-extension", "valentjn.vscode-ltex"],
        )
