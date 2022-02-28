import webbrowser
from ..redirect.start import redirect_port
import socket
from time import sleep

def _wait(port: int) -> None:
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        if result == 0:
            break
        sleep(10)

def browser(name: str, **kwargs: str) -> None:
    """
    redirect ports to a Virtual Machine and launch browser

    Args:
        name (str): Virtual Machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name and port numbers (default 8080=8080)

    Returns:
        None

    """
    proc, port = redirect_port(name, **kwargs, wait=False)
    controller = webbrowser.get()
    _wait(int(port))
    controller.open_new(f'http:localhost:{port}')
 
