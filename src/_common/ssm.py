import os
import sys
import subprocess
import instance
from _common.session import get_session, Session

def _make_env(session: Session) -> dict:
    credentials = session.get_credentials()
    return {
        **os.environ,
        **dict(
            AWS_ACCESS_KEY_ID=credentials.access_key,
            AWS_SECRET_ACCESS_KEY=credentials.secret_key,
            AWS_SESSION_TOKEN=credentials.token,
            AWS_DEFAULT_REGION=session.region_name
        )
    }
    
def _start_ssm_session(instance_id: str, env: dict, wait: bool, *args: str) -> subprocess.Popen:
    proc = subprocess.Popen(
        args=[
            'aws',
            'ssm',
            'start-session',
            '--target',
            instance_id,
            *args
        ],
        env=env
    )
    if wait:
        proc.wait()
        if 0 != proc.returncode:
            print(proc.stderr)
            sys.exit(proc.returncode)
    return proc

    
def start_session(instance_name: str, *args: str, **kwargs: str) -> subprocess.Popen:
    """
    Start ssm session

    Args:
        instance_name (str): Virtual Machine instance name
        *args (str): (optional) list of additional arguments to be passed to ssm
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None

    """
    session, instance_id = instance.start(instance_name, **kwargs)
    return _start_ssm_session(
        instance_id, 
        _make_env(session), 
        kwargs.get('wait', True),
        *args
    )

def terminate_session(session_id: str, **kwargs: str) -> None:
    """
    Terminate ssm session

    Args:
        session_id (str): SSM session ID
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None

    """
    proc = subprocess.Popen(
        args=[
            'aws',
            'ssm',
            'terminate-session',
            '--session-id',
            session_id,
        ],
        env=_make_env(get_session(kwargs.get('profile', 'default')))
    )
    proc.wait()
    if 0 != proc.returncode:
        print(proc.stderr)
        sys.exit(proc.returncode)
    
