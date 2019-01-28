""" Default Application Entry Point """

import sys
import PyQt5.QtWidgets

from communications import udp_conn
from controller import gamepad as gp
from mainwindow import window_main as wm
from settings import settings


# TODO, taskbar icon not displaying currently? Why?
def loadAppIcon():
    """Load application default icon, for all windows + taskbar"""
    app_icon = PyQt5.QtGui.QIcon()
    app_icon.addFile('images/logo_16.png', PyQt5.QtCore.QSize(16, 16))
    app_icon.addFile('images/logo_24.png', PyQt5.QtCore.QSize(24, 24))
    app_icon.addFile('images/logo_32.png', PyQt5.QtCore.QSize(32, 32))
    app_icon.addFile('images/logo_48.png', PyQt5.QtCore.QSize(48, 48))
    app_icon.addFile('images/logo_256.png', PyQt5.QtCore.QSize(256, 256))
    app_icon.addFile('images/logo.png', PyQt5.QtCore.QSize(512, 512))
    return app_icon


if __name__ == "__main__":
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(loadAppIcon())
    settings.loadSettings()
    conn = udp_conn.connectToRoverServer()
    xbox = gp.loadGamepad()
    mainwnd = wm.loadMainWindow()
    sys.exit(app.exec_())
