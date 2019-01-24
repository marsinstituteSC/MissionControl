""" Default Application Entry Point """

import sys
import PyQt5.QtWidgets

from communications import udp_conn
from controller import gamepad as gp
from mainwindow import window_main as wm
from settings import settings

if __name__ == "__main__":
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    settings.loadSettings()
    conn = udp_conn.connectToRoverServer()
    xbox = gp.loadGamepad()
    mainwnd = wm.loadMainWindow()
    sys.exit(app.exec_())
