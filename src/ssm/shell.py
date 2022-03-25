import time
import instance
from typing import Tuple


def shell(instance_name: str, *commands: str, **kwargs: str) -> Tuple[str, str]:
    """
    Execure shell script over ssm channel

    Args:
        instance_name (str): Virtual Machine instance name
        *commands (str): (optional) list of additional arguments to be passed to ssm
        **kwargs (str): (optional) classifiers, at the moment, profile name, delay (dafult 5), number of attempts (20)

    Returns:
        standard output, standard err

    """
    session, instance_id = instance.start(instance_name, **kwargs)
    ssm_client = session.client('ssm')
    result = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName='AWS-RunShellScript',
        Parameters={
            'commands': [
                'source /etc/bashrc',
                *commands
            ]
        }
    )
    command_id = result.Command.CommandId
    waiter = ssm_client.get_waiter('command_executed')
    # see https://stackoverflow.com/questions/50067035/retrieving-command-invocation-in-aws-ssm
    time.sleep(2)
    try:
        waiter.wait(
            CommandId=command_id,
            InstanceId=instance_id,
            WaiterConfig={
                'Delay': kwargs.get('delay', 5),
                'MaxAttempts': kwargs.get('attempts', 20)
            }
        )
    finally:
        result = ssm_client.get_command_invocation(
            CommandId=command_id,
            InstanceId=instance_id,
            PluginName='aws:RunShellScript'
        )
        print(result.StandardOutputContent)
        print(result.StandardErrorContent)
    return result.StandardOutputContent, result.StandardErrorContent
