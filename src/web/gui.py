from PyQt5.QtCore import QUrl
from ..redirect.start import redirect_port
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
import psutil

# creating main window class
class MainWindow(QMainWindow):
 
    # constructor
    def __init__(self, name: str, port: str) -> None:
        super().__init__()
 
        self._name = name

        # creating a QWebEngineView
        self.browser = QWebEngineView()

        # setting default browser url as google
        self.browser.setUrl(QUrl(f"http://localhost:{port}"))

        # adding action when loading is finished
        self.browser.loadFinished.connect(self.update_title)

        # set this browser as central widget or main window
        self.setCentralWidget(self.browser)

        # showing all the components
        self.showMaximized()


    # method for updating the title of the window
    def update_title(self):
        title = self.browser.page().title()
        self.setWindowTitle(self._name)


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
    # creating a pyQt5 application
    app = QApplication([])
     
    # setting name to the application
    app.setApplicationName(name)
    proc, port = redirect_port(name, **kwargs, wait=False)
    _wait(int(port))
 
    # creating a main window object
    window = MainWindow(name, port)

    # loop
    app.exec_()
    parent = psutil.Process(proc.pid)
    for child in parent.children(recursive=True):
        child.kill()
    parent.kill()
    
