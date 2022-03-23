import os
import sys
import subprocess
from _common.session import get_session

def vscode(**kwargs: str) -> None:
    """
    Obtain token and start instance if required and launch vscode editor

    Args:
        **kwargs (str): (optional) classifiers, at the moment, profile name

    Returns:
        None

    """
    get_session(kwargs.get('profile', 'default'))  # TODO: eliminate duplication
    subprocess.Popen(
        args=[
            'code'
        ]
    )

