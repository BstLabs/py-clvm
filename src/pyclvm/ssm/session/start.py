import os
import subprocess
import sys
from typing import Union

from pyclvm._common.session import Session
from pyclvm._common.signal_handler import interrupt_handler
from pyclvm.instance import start as instance_start


def _make_env(session: Session) -> dict:
    credentials = session.get_credentials()
    return {
        **os.environ,
        **{
            "AWS_ACCESS_KEY_ID": credentials.access_key,
            "AWS_SECRET_ACCESS_KEY": credentials.secret_key,
            "AWS_SESSION_TOKEN": credentials.token,
            "AWS_DEFAULT_REGION": session.region_name,
        },
    }


def _call_subprocess(instance_id: str, env: dict, wait: Union[str, bool], *args: str):
    proc = subprocess.Popen(
        args=["aws", "ssm", "start-session", "--target", instance_id, *args],
        env=env,
    )
    if wait:
        proc.wait()
        if proc.returncode != 0:
            print(proc.stderr)
            sys.exit(proc.returncode)
    return proc


def _start_ssm_session(
    instance_id: str, env: dict, wait: Union[str, bool], *args: str
) -> subprocess.Popen:
    with interrupt_handler():
        return _call_subprocess(instance_id, env, wait, *args)


def start(instance_name: str, *args: str, **kwargs: str) -> subprocess.Popen:
    """
    Start ssm session

    Args:
        instance_name (str): Virtual Machine instance name
        *args (str): (optional) list of additional arguments to be passed to ssm
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None

    """
    try:
        session, instance_id = instance_start(instance_name, **kwargs)
        return _start_ssm_session(
            instance_id, _make_env(session), kwargs.get("wait", True), *args
        )
    except RuntimeError as err:
        print(err)
