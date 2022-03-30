import webbrowser

from pyclvm.redirect import start


def browser(name: str, **kwargs: str) -> None:
    """
    redirect ports to a Virtual Machine and launch browser

    Args:
        name (str): Virtual Machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name and port numbers (default 8080=8080)

    Returns:
        None

    """
    local_port = start(name, **kwargs)
    controller = webbrowser.get()
    controller.open_new(f"http:localhost:{local_port}")
