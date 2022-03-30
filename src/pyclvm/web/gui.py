from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow

from pyclvm import redirect


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
        self.browser.page().title()
        self.setWindowTitle(self._name)


def gui(instance_name: str, **kwargs: str) -> None:
    """
    redirect ports to a Virtual Machine and launch embedded browser

    Args:
        instance_name (str): Virtual Machine instance name
        **kwargs (str): (optional) classifiers, at the moment, profile name and port numbers (default 8080=8080)

    Returns:
        None

    """
    # creating a pyQt5 application
    app = QApplication([])

    # setting name to the application
    app.setApplicationName(instance_name)

    # start port redirection
    local_port = redirect.start(instance_name, **kwargs)

    # creating a main window object
    _ = MainWindow(
        instance_name, local_port
    )  # need to assign to a variable to prevent it from being stuck (stange)

    # loop
    app.exec_()

    # stop port redirection
    redirect.stop(instance_name, **kwargs)
