import contextlib
import getpass
import os
import platform
import sys
from functools import partial
from os.path import exists, expanduser, join
from shutil import copyfile, copymode, move
from tempfile import mkstemp
from typing import Dict, Final, List, Tuple, Union

from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from ec2instances.ec2_instance_mapping import Ec2RemoteShellMapping, Ec2RemoteShellProxy

from pyclvm._common.azure_instance_mapping import (
    AzureRemoteShellMapping,
    AzureRemoteShellProxy,
)
from pyclvm._common.azure_instance_proxy import next_free_port
from pyclvm._common.gcp_instance_mapping import (
    GcpRemoteShellMapping,
    GcpRemoteShellProxy,
)
from pyclvm._common.session_aws import get_session
from pyclvm.plt import (
    _default_platform,
    _get_supported_platforms,
    _unsupported_platform,
)

_SSH_DIR: Final[str] = expanduser(join("~", ".ssh"))
_SSH_CONFIG: Final[str] = join(_SSH_DIR, "config")

_GOOGLE_SSH_PRIV_KEY_NAME: Final[str] = "google_compute_engine"
_GOOGLE_SSH_PRIV_KEY: Final[str] = f"{_SSH_DIR}/{_GOOGLE_SSH_PRIV_KEY_NAME}"
_GOOGLE_SSH_PUB_KEY: Final[str] = f"{_SSH_DIR}/{_GOOGLE_SSH_PRIV_KEY_NAME}.pub"
_GOOGLE_SSH_KNOWN_HOSTS: Final[str] = f"{_SSH_DIR}/google_compute_known_hosts"

_BACKUP_SUFFIX = "ORIG"
_MAIN = sys.modules["__main__"].__file__
_PLATFORM = _default_platform().lower()


def new(instance_name: str, **kwargs: str) -> Union[Dict, None]:
    """
    create new ssh key for particular Virtual Machine

    Args:
        instance_name (str): Virtual Machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name, also look at shell

    Returns:
        None
    """
    default_platform, supported_platforms = (
        _default_platform(**kwargs),
        _get_supported_platforms(),
    )

    if default_platform in supported_platforms:
        return {
            "AWS": partial(_new_aws, instance_name, **kwargs),
            "GCP": partial(_new_gcp, instance_name, **kwargs),
            "AZURE": partial(_new_azure, instance_name, **kwargs),
        }[default_platform.upper()]()
    else:
        _unsupported_platform(default_platform)


# ---
def _new_aws(instance_name: str, **kwargs: str) -> None:
    instance = Ec2RemoteShellMapping(get_session(kwargs)).get(instance_name)
    _create_config_block(instance=instance, **kwargs)


# ---
def _new_gcp(instance_name: str, **kwargs: str) -> None:
    instance = GcpRemoteShellMapping().get(instance_name)
    _create_config_block(instance=instance, **kwargs)


# ---
def _new_azure(instance_name: str, **kwargs: str) -> None:
    instance = AzureRemoteShellMapping().get(instance_name)
    _create_config_block(instance=instance, **kwargs)


# ---
def _aws_config_lines(instance: Ec2RemoteShellProxy, **kwargs: str):
    profile = kwargs.get("profile", "default")
    private_key_name, pubkey = _save_keys(profile, instance.name)

    proxy_data = {
        "identity_file": private_key_name,
        "proxy_command": f"{str(_MAIN)} ssh start {instance.name} %p profile={profile} platform={_PLATFORM}",
        "user_name": "ssm-user",
    }
    instance.execute(
        "pip3 install --upgrade authk",
        f'runuser -u ssm-user -- authk add "{pubkey}"',
        **kwargs,
    )
    return _config_lines(instance.name, proxy_data)


# ---
def _gcp_config_lines(instance: GcpRemoteShellProxy, **kwargs: str):
    return _config_lines(
        instance.name, _get_gcp_proxy_data(instance=instance, **kwargs)
    )


# ---
def _azure_config_lines(instance: AzureRemoteShellProxy, **kwargs: str) -> List:
    profile = kwargs.get("profile", "default")

    account = kwargs.get("account")
    key = kwargs.get("key")
    if not account or not key:
        print(
            "\n------------\nSpecify account=account_name or/and key=/path/to/ssh/key/file\n"
            'e.g "clvm ssh new vm-instance-name account=username '
            'key=/path/to/ssh/key/file platform=azure"\n'
        )
        sys.exit(-1)

    port = next_free_port(port=22060, max_port=22960)
    proxy_data = {
        "identity_file": key,
        "proxy_command": f"{str(_MAIN)} ssh start {instance.name} {port} profile={profile} platform={_PLATFORM}",
        "user_name": account,
    }
    return _config_lines(instance.name, proxy_data)


# ---------------------------------
# --- Generate new SSH key pair ---
def _format_public_key(pubkey) -> str:
    return f'{pubkey.decode("utf-8")} {getpass.getuser()}@{platform.node()}'


def _generate_keys() -> Tuple[str, str]:
    key = rsa.generate_private_key(
        backend=crypto_default_backend(), public_exponent=65537, key_size=2048
    )

    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption(),
    )

    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.OpenSSH, crypto_serialization.PublicFormat.OpenSSH
    )
    return private_key.decode("utf-8"), _format_public_key(public_key)


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


# --- End of Generate new SSH key pair ---
# ----------------------------------------


# ----------------------------------------
# --- Analysis and writing config file ---
def _analyze_config(instance_name: str, _platform: str) -> Tuple[int, int]:
    previous_conf_pos = -1
    wildcard_conf_pos = -1
    with open(_SSH_CONFIG, "r", encoding="utf8") as config_file:
        lines = config_file.readlines()
        for line_number, line_text in enumerate(lines):
            if f"Host {instance_name}-{_platform}" == line_text.strip():
                previous_conf_pos = line_number
            if line_text.strip() == "Host *":
                wildcard_conf_pos = line_number

    return previous_conf_pos, wildcard_conf_pos


# ---
def _config_lines(instance_name: str, proxy_data: Dict) -> List:
    lines = [
        f"Host {instance_name}-{_PLATFORM}\n",
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
    with contextlib.suppress(FileNotFoundError):
        backup_file = f"{file}.{_BACKUP_SUFFIX}"
        copyfile(file, backup_file)
        os.chmod(backup_file, perm)


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
def _create_config_block(
    instance: Union[GcpRemoteShellProxy, AzureRemoteShellProxy, Ec2RemoteShellProxy],
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
    config_lines = {
        "aws": partial(_aws_config_lines, instance, **kwargs),
        "gcp": partial(_gcp_config_lines, instance, **kwargs),
        "azure": partial(_azure_config_lines, instance, **kwargs),
    }[_PLATFORM]()

    os.makedirs(name=_SSH_DIR, mode=0o700, exist_ok=True)

    if os.path.isfile(_SSH_CONFIG):
        _backup(_SSH_CONFIG, 0o600)
        _update_config(
            instance_name=instance.name, config_lines=config_lines, _platform=_PLATFORM
        )
    else:
        with open(
            os.open(_SSH_CONFIG, os.O_CREAT | os.O_WRONLY, 0o600), "w", encoding="utf8"
        ) as config_file:
            [config_file.write(line) for line in config_lines]


# --- End of Analysis and writing config file ---
# -----------------------------------------------


# -------------------------------------------------
# --- Special for Google SDK extract proxy data ---
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
    profile = kwargs.get("profile", "default")
    kwargs["dry_run"] = "yes"
    kwargs["capture_output"] = True
    _stdout = instance.execute((), **kwargs).stdout.decode("utf8")
    try:
        _stdout.index("ProxyCommand") + 13
        # ind_2 = _stdout.index('" -o ProxyUseFdpass=no')

        account = kwargs.get("account")
        if not account:
            raise ValueError(
                "No username/account, use [--account=username@company.com]"
            )
        for c in ("@", ".", "-"):
            account = account.replace(c, "_")

        return {
            "identity_file": _GOOGLE_SSH_PRIV_KEY,
            # "proxy_command": _stdout[ind_1:ind_2],
            "proxy_command": f"{str(_MAIN)} ssh start {instance.name} %p profile={profile} platform={_PLATFORM}",
            "user_name": account[:32].strip(
                "_"
            ),  # Google OSLogin account name length is <= 32 without
            # underline sign at the end
        }
    except ValueError:
        print(
            "\n------------\nNo such VM name or/and account. Set the existing VM name or/and account.\n"
            'e.g "clvm ssh new vm-instance-name account=username@domain.com platform=gcp"\n'
        )
        sys.exit(-1)


# --- End of Special for Google SDK extract proxy data ---
# --------------------------------------------------------
