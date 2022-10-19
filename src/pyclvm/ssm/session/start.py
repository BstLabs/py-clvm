"""start ssm session"""

import os
import sys
from subprocess import Popen, TimeoutExpired
from typing import Optional

from ec2instances.common.session import Session
from ec2instances.common.signal_handler import interrupt_handler

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


def _call_subprocess(instance_id: str, env: dict, wait: bool, *args: str):
    proc = Popen(
        args=["aws", "ssm", "start-session", "--target", instance_id, *args],
        env=env,
    )
    if wait:
        proc.wait()
        if proc.returncode != 0:
            try:
                outs, errs = proc.communicate(timeout=15)
            except TimeoutExpired:
                proc.kill()
                outs, errs = proc.communicate()
            print(errs, outs, sep="\n")
            sys.exit(proc.returncode)
    return proc


def _start_ssm_session(instance_id: str, env: dict, wait: bool, *args: str) -> Popen:
    with interrupt_handler():
        return _call_subprocess(instance_id, env, wait, *args)


def start(instance_name: str, *args: str, **kwargs: str) -> Optional[Popen]:
    """
    start ssm session

    Args:
        instance_name (str): Virtual Machine instance name
        *args (str): (optional) list of additional arguments to be passed to ssm
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None

    """
    try:
        session, instance_id = instance_start(
            instance_name,
            **dict(kwargs, wait=True),
        )  # type: ignore
        return _start_ssm_session(instance_id, _make_env(session), True, *args)
    except RuntimeError as err:
        print(err)
        return None
