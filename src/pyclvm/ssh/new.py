import getpass
import os
import platform
from os.path import exists, expanduser, join
from typing import Final, Tuple

from Crypto.PublicKey import RSA
from sshconf import empty_ssh_config_file, read_ssh_config

from pyclvm.ssm import shell

_SSH_DIR: Final[str] = expanduser(join("~", ".ssh"))
_SSH_CONFIG: Final[str] = join(_SSH_DIR, "config")


def _format_public_key(pubkey) -> str:
    return f'{pubkey.exportKey(r"OpenSSH").decode("utf-8")} {getpass.getuser()}@{platform.node()}'


def _generate_keys() -> Tuple[str, str]:
    key = RSA.generate(1024)
    pubkey = key.publickey()
    return key.exportKey("PEM").decode("utf-8"), _format_public_key(pubkey)


def _save_keys(profile: str, instance_name: str) -> Tuple[str, str]:
    private_key_name = f"{join(_SSH_DIR,'aws')}-{profile}-{instance_name}"
    public_key_name = f"{private_key_name}.pub"
    key, pubkey = _generate_keys()

    if exists(private_key_name):
        os.chmod(private_key_name, 0o600)

    if not exists(_SSH_DIR):
        os.mkdir(_SSH_DIR)

    with open(private_key_name, "w", encoding="utf-8") as f:
        f.write(key)
    os.chmod(private_key_name, 0o400)

    with open(public_key_name, "w", encoding="utf-8") as f:
        f.write(pubkey)

    return private_key_name, pubkey


def _update_ssh_config(instance_name: str, private_key_name: str, profile: str) -> None:
    try:
        c = read_ssh_config(_SSH_CONFIG)
    except FileNotFoundError:
        c = empty_ssh_config_file()
    params = {
        "IdentityFile": private_key_name,
        "ProxyCommand": f"clvm ssh start %h %p profile={profile}",
        "User": "ssm-user",
    }
    func = c.set if c.host(instance_name) else c.add
    func(instance_name, **params)
    c.write(_SSH_CONFIG)


def new(instance_name: str, **kwargs: str) -> None:
    """
    create new ssh key for particular Virtual Machine

    Args:
        instance_name (str): Virtual Machine instance name
        port (int): port number
        **kwargs (str): (optional) classifiers, at the moment, profile name, also look at shell

    Returns:
        None
    """
    profile = kwargs.get("profile", "default")
    private_key_name, pubkey = _save_keys(profile, instance_name)
    _update_ssh_config(instance_name, private_key_name, profile)
    shell(
        instance_name,
        "pip3 install --upgrade authk",
        f'runuser -u ssm-user -- authk add "{pubkey}"',
        **kwargs,
    )
