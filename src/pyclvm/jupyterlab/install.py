from ssm import shell


def install(instance_name: str, **kwargs: str) -> None:
    """
    install/update jupyter lab at particular Virtual Machine

    Args:
        instance_name (str): Virtual Machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name, also look at shell

    Returns:
        None
    """
    shell(instance_name, "sudo pip3 install --upgrade jupyterlab", **kwargs)
