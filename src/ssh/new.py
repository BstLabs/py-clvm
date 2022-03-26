import getpass
import platform
from ssm import shell
from os.path import expanduser
from typing import Final, Tuple
from Crypto.PublicKey import RSA
from sshconf import read_ssh_config, empty_ssh_config_file


_SSH_DIR: Final[str] = expanduser("~/.ssh")
_SSH_CONFIG: Final[str] = f'{_SSH_DIR}/config'


def _format_public_key(pubkey) -> str:
    return f'{pubkey.exportKey(r"OpenSSH").decode("utf-8")} {getpass.getuser()}@{platform.node()}'


def _generate_keys() -> Tuple[str, str]:
    key = RSA.generate(1024)
    pubkey = key.publickey()
    return key.exportKey('PEM').decode('utf-8'), _format_public_key(pubkey)


def _save_keys(profile: str, instance_name: str) -> Tuple[str, str]:
    private_key_name = f'{_SSH_DIR}/aws-{profile}-{instance_name}'
    public_key_name = f'{private_key_name}.pub'
    key, pubkey = _generate_keys()

    with open(private_key_name, "w") as f:
        f.write(key)

    with open(public_key_name, "w") as f:
        f.write(pubkey)

    return private_key_name, pubkey


def _update_ssh_config(instance_name: str, private_key_name: str) -> None:
    try:
        c = read_ssh_config(_SSH_CONFIG)
    except FileNotFoundError:
        c = empty_ssh_config_file()
    params = dict(IdentityFile=private_key_name, ProxyCommand=f'{expanduser("~/clvm/clvm")} ssh start %h %p')
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
    profile = kwargs.get('profile', 'default')
    private_key_name, pubkey = _save_keys(profile, instance_name)

    _update_ssh_config(instance_name, private_key_name)
    shell(instance_name, f'/home/ssm-user/authk/authk add "{pubkey}"', **kwargs)
