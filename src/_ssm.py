import os
import sys
import subprocess
from typing import Type
from _session import get_session
from boto3.session import Session

Instance = Type['Instance']  # impossible to import statically from boto3

def _get_instance(session: Session, name: str) -> Instance:
    ec2_client = session.client('ec2')
    ec2_resource = session.resource('ec2')
    instances = ec2_client.describe_instances(
        Filters=[
            dict(Name='tag:Name', Values=[name]) 
        ]
    )
    instance = ec2_resource.Instance(instances.Reservations[0].Instances[0].InstanceId)
    return instance

def _start_instance(instance: Instance) -> None:
    if 'stopped' == instance.state.Name:
        print('Starting instance ...')
        instance.start()
        instance.wait_until_running()
    print('Instance running')

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

    
def start_session(name:str, *args: str, **kwargs: str) -> subprocess.Popen:
    """
    Start ssm session

    Args:
        name (str): Virtual Machine instance name
        *args (str): (optional) list of additional arguments to be passed to ssm
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None

    """
    session = get_session()
    instance = _get_instance(session, name)
    _start_instance(instance)
    return _start_ssm_session(
        instance.instance_id, 
        _make_env(session), 
        kwargs.get('wait', True),
        *args
    )
    
