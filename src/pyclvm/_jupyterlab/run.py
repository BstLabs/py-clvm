from pyclvm._web import gui
from pyclvm.ssm import shell


def run(instance_name: str, **kwargs: str) -> None:
    """
    run jupyter lab at particular Virtual Machine

    Args:
        instance_name (str): Virtual Machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name, also look at shell and web/gui

    Returns:
        None
    """
    # TODO: check is jupyter is running mb keep_running=True ???
    ssm_client, command_id, instance_id = shell(
        instance_name,
        "runuser -u ssm-user -- jupyter-lab --notebook-dir /home/ssm-user/ &\n",
        wait=False,
        **kwargs,
    )

    gui(instance_name, **{**kwargs, **{"8888": "8888"}})  # be surprised, but it works

    if kwargs.get("keep_instance", False):
        ssm_client.cancel_command(CommandId=command_id, InstanceIds=[instance_id])
        shell(  # TODO: optimize
            instance_name, "runuser -u ssm-user -- jupyter lab list", **kwargs
        )
