import webbrowser

from pyclvm import redirect


def browser(name: str, **kwargs: str) -> None:
    """
    redirect ports to a virtual machine and launch browser

    Args:
        name (str): Virtual Machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name and port numbers (default 8080=8080)

    Returns:
        None

    """
    local_port = redirect.start(name, **kwargs)
    controller = webbrowser.get()
    controller.open_new(f"http:localhost:{local_port}")
