import getpass
import os
import platform
from functools import partial
from os.path import exists, expanduser, join
from shutil import copyfile, copymode, move
from tempfile import mkstemp
from typing import Dict, Final, List, Tuple, Union

from Crypto.PublicKey import RSA
from ec2instances.ec2_instance_mapping import Ec2RemoteShellMapping
from sshconf import empty_ssh_config_file, read_ssh_config

from pyclvm._common.azure_instance_mapping import (
    AzureRemoteShellMapping,
    AzureRemoteShellProxy,
)
from pyclvm._common.azure_instance_proxy import next_free_port
from pyclvm._common.gcp_instance_mapping import (
    GcpRemoteShellMapping,
    GcpRemoteShellProxy,
)
from pyclvm._common.session import get_session
from pyclvm.plt import _default_platform, _unsupported_platform

_SSH_DIR: Final[str] = expanduser(join("~", ".ssh"))
_SSH_CONFIG: Final[str] = join(_SSH_DIR, "config")

_GOOGLE_SSH_PRIV_KEY_NAME: Final[str] = "google_compute_engine"
_GOOGLE_SSH_PRIV_KEY: Final[str] = f"{_SSH_DIR}/{_GOOGLE_SSH_PRIV_KEY_NAME}"
_GOOGLE_SSH_PUB_KEY: Final[str] = f"{_SSH_DIR}/{_GOOGLE_SSH_PRIV_KEY_NAME}.pub"
_GOOGLE_SSH_KNOWN_HOSTS: Final[str] = f"{_SSH_DIR}/google_compute_known_hosts"

_BACKUP_SUFFIX = "ORIG"


def _format_public_key(pubkey) -> str:
    return f'{pubkey.exportKey(r"OpenSSH").decode("utf-8")} {getpass.getuser()}@{platform.node()}'


def _generate_keys() -> Tuple[str, str]:
    key = RSA.generate(1024)
    pubkey = key.publickey()
    return key.exportKey("PEM").decode("utf-8"), _format_public_key(pubkey)


def _save_keys(profile: str, instance_name: str) -> Tuple[str, str]:
    private_key_name = f"{join(_SSH_DIR, 'aws')}-{profile}-{instance_name}"
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


def new(instance_name: str, **kwargs: str) -> Union[Dict, None]:
    """
    create new ssh key for particular Virtual Machine

    Args:
        instance_name (str): Virtual Machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name, also look at shell

    Returns:
        None
    """
    platform, supported_platforms = _default_platform(**kwargs)

    if platform in supported_platforms:
        return {
            "AWS": partial(_new_aws, instance_name, **kwargs),
            "GCP": partial(_new_gcp, instance_name, **kwargs),
            "AZURE": partial(_new_azure, instance_name, **kwargs),
        }[platform.upper()]()
    else:
        _unsupported_platform(platform)


# ---
def _new_aws(instance_name: str, **kwargs: str) -> None:
    instance = Ec2RemoteShellMapping(get_session(kwargs))[instance_name]
    profile = kwargs.get("profile", "default")
    private_key_name, pubkey = _save_keys(profile, instance_name)
    _update_ssh_config(instance_name, private_key_name, profile)
    instance.execute(
        "pip3 install --upgrade authk",
        f'runuser -u ssm-user -- authk add "{pubkey}"',
        **kwargs,
    )


# ---
def _new_gcp(instance_name: str, **kwargs: str) -> None:
    instance = GcpRemoteShellMapping().get(instance_name)
    _create(instance_name=instance_name, instance=instance, **kwargs)


# ---
def _new_azure(instance_name: str, **kwargs: str) -> None:
    instance = AzureRemoteShellMapping().get(instance_name)
    _create(instance_name=instance_name, instance=instance, **kwargs)


# ----------------------
# ----------------------
# ----------------------
def _get_gcp_proxy_data(instance: GcpRemoteShellProxy, **kwargs: str) -> Dict:
    """
    Gets proxy string and real GCP instance's username
    Args:
        instance (str): The name of an instance to run
        username (str): The name of a user to log in to the instance
        **kwargs (str): (optional) additional arguments
    Returns:
        (jdict) Retrieved data
    """

    kwargs["dry_run"] = "yes"
    kwargs["capture_output"] = True
    _stdout = instance.execute((), **kwargs).stdout.decode("utf8")
    try:
        ind_1 = _stdout.index("ProxyCommand") + 13
        ind_2 = _stdout.index('" -o ProxyUseFdpass=no')

        account = kwargs.get("account")
        if not account:
            raise ValueError(
                "No username/account, use [--account=username@company.com]"
            )
        for c in ("@", ".", "-"):
            account = account.replace(c, "_")

        return {
            "identity_file": _GOOGLE_SSH_PRIV_KEY,
            "proxy_command": _stdout[ind_1:ind_2],
            "user_name": account[:32].strip("_"),
        }
    except ValueError:
        raise RuntimeError(
            "\n------------\nNo such VM name or/and account. Set the existing VM name and account.\n"
            'e.g "clvm ssh new vm-instance-name account=username@domain.com platform=gcp"\n'
        )


# ---
def _analyze_config(instance_name: str, _platform: str) -> Tuple[int, int]:
    previous_conf_pos = -1
    wildcard_conf_pos = -1
    with open(_SSH_CONFIG, "r", encoding="utf8") as config_file:
        lines = config_file.readlines()
        for line_number, line_text in enumerate(lines):
            if f"Host {instance_name}-{_platform}" == line_text.strip():
                previous_conf_pos = line_number
            if "Host *" == line_text.strip():
                wildcard_conf_pos = line_number

    return previous_conf_pos, wildcard_conf_pos


# ---
def _config_lines(instance_name: str, proxy_data: Dict, _platform: str) -> List:
    lines = [
        f"Host {instance_name}-{_platform}\n",
        f"  IdentityFile {proxy_data['identity_file']}\n",
        f"  ProxyCommand {proxy_data['proxy_command']}\n",
        f"  User {proxy_data['user_name']}\n",
    ]
    if "port" in proxy_data.keys():
        lines.append(f"  Port {proxy_data['port']}\n")
    return lines


# ---
def _backup(file: str, perm: int) -> None:
    """
    Backs up current SSH configuration file
    """
    try:
        backup_file = f"{file}.{_BACKUP_SUFFIX}"
        copyfile(file, backup_file)
        os.chmod(backup_file, perm)
    except FileNotFoundError:
        pass


# ---
def _write(position: int, config_lines: List, skip_updated_text: bool):
    tmp_file, tmp_file_path = mkstemp()
    skip_flag = True

    with os.fdopen(tmp_file, "w", encoding="utf8") as dst_file:
        with open(_SSH_CONFIG) as src_file:
            if position < 0:
                position = len(src_file.readlines()) - 1
                src_file.seek(0)
            for line_num, line_text in enumerate(src_file):
                if line_num == position:
                    if "" == line_text.strip():
                        dst_file.write("\n")

                    [dst_file.write(line) for line in config_lines]
                    skip_flag = skip_updated_text
                    dst_file.write("\n")

                    if skip_flag:
                        dst_file.write(line_text)
                else:
                    if not skip_flag:
                        if "Host" == line_text[:4]:
                            dst_file.write(line_text)
                            skip_flag = True
                    else:
                        dst_file.write(line_text)
    # copy the file permissions from the old file to the new file
    copymode(_SSH_CONFIG, tmp_file_path)
    # remove original file
    os.remove(_SSH_CONFIG)
    # move new file
    move(tmp_file_path, _SSH_CONFIG)


# ---
def _update_config(instance_name: str, config_lines: List, _platform: str) -> None:
    previous_conf_pos, wildcard_conf_pos = _analyze_config(instance_name, _platform)
    if previous_conf_pos < 0:
        if wildcard_conf_pos < 0:
            # write to the end of file
            _write(
                previous_conf_pos,
                config_lines=config_lines,
                skip_updated_text=True,
            )
        else:
            # write before wildcard line
            _write(
                wildcard_conf_pos,
                config_lines=config_lines,
                skip_updated_text=True,
            )
    else:
        # update lines from the position
        _write(
            previous_conf_pos,
            config_lines=config_lines,
            skip_updated_text=False,
        )


# ---
def _create(
    instance_name: str,
    instance: Union[GcpRemoteShellProxy, AzureRemoteShellProxy],
    **kwargs: str,
) -> None:
    """
    Creates or updates SSH configuration file

    Args:
        instance_name (str): The name of an instance to run
        username (str): The name of a user to log in to the instance
        **kwargs (str): (optional) additional arguments
    Returns:
        None
    """
    _platform = ""
    config_lines = []
    if isinstance(instance, GcpRemoteShellProxy):
        _platform = "gcp"
        config_lines = _config_lines(
            instance_name, _get_gcp_proxy_data(instance=instance, **kwargs), _platform
        )
    elif isinstance(instance, AzureRemoteShellProxy):
        _platform = "azure"
        config_lines = _azure_config_lines(instance_name, **kwargs)

    os.makedirs(name=_SSH_DIR, mode=0o700, exist_ok=True)

    if os.path.isfile(_SSH_CONFIG):
        _backup(_SSH_CONFIG, 0o600)
        _update_config(
            instance_name=instance_name, config_lines=config_lines, _platform=_platform
        )
    else:
        with open(
            os.open(_SSH_CONFIG, os.O_CREAT | os.O_WRONLY, 0o600), "w", encoding="utf8"
        ) as config_file:
            [config_file.write(line) for line in config_lines]


# ---
def _azure_config_lines(instance_name: str, **kwargs: str) -> List:
    instance = AzureRemoteShellMapping().get(instance_name)

    _account = kwargs.get("account")
    _key = kwargs.get("key")
    if not _account or not _key:
        raise RuntimeError(
            "\n------------\nSpecify account=account_name or/and key=/path/to/ssh/key/file\n"
            'e.g "clvm ssh new vm-instance-name account=username '
            'key=/path/to/ssh/key/file platform=azure"\n'
        )

    _port = next_free_port(port=22060, max_port=22160)
    instance_name = instance.name
    proxy_data = {
        "identity_file": _key,
        "proxy_command": f"clvm ssh start {instance_name} {_port} platform=azure",
        "user_name": _account,
    }
    return _config_lines(instance_name, proxy_data, "azure")
