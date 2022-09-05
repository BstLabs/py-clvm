from typing import Any, Tuple, Union

from ec2instances.ec2_instance_mapping import Ec2RemoteShellMapping

from pyclvm._common.session_aws import get_session


def shell(
    instance_name: str, *commands: str, **kwargs: str
) -> Union[Tuple[str, str], Tuple[Any, str, str]]:
    """

    execute shell script over ssm channel


    Args:
        instance_name (str): Virtual Machine instance name
        *commands (str): (optional) list of additional arguments to be passed to ssm
        **kwargs (str): (optional) classifiers, at the moment, profile name, delay (dafult 5), number of attempts (20), whether to wait for completion

    Returns:
        standard output, standard err if wait=True (default), otherwise ssm_client, command_id, instance_id

    """
    instance = Ec2RemoteShellMapping(get_session(kwargs))[instance_name]
    return instance.execute(*commands)  # type: ignore
