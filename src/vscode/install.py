import sys
import subprocess
import platform
from typing import List


# TODO: form it at install time- no reason to detect platform dynamically
# TODO: provide support for Mac, Windows, CentOS

def _run_script(*commands: List[str]) -> None:
    #TODO: generic open source?
    for command in commands:
        try:
            print(' '.join(command))
            subprocess.run(command, check=True)
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
    assert 'Linux' == env.system
    assert 'Ubuntu' in env.version
    assert 'x86_64' == env.machine
    _run_script(
        ['sudo', 'apt', 'update'],
        ['sudo', 'apt', 'install', '-y', 'software-properties-common', 'apt-transport-https', 'wget'],
        ['wget', '-q', 'https://packages.microsoft.com/keys/microsoft.asc', '-O', '/tmp/microsoft.asc'],
        ['sudo', 'apt-key', 'add', '/tmp/microsoft.asc'],
        ['sudo', 'add-apt-repository', "deb [arch=amd64] https://packages.microsoft.com/repos/vscode stable main"],
        ['sudo', 'apt', 'install', '-y', 'code'],
        ['code', '--install-extension', 'ms-vscode.makefile-tools'],
        ['code', '--install-extension', 'ms-python.python'],
        ['code', '--install-extension', 'ms-vscode-remote.remote-ssh'],
        ['code', '--install-extension', 'valentjn.vscode-ltex']
    )
    
