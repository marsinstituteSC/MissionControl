""" Default Application Entry Point """

import sys
import PyQt5.QtWidgets
import qdarkstyle

from communications import udp_conn
from controller import gamepad as gp
from mainwindow import window_main as wm
from utils import event
from settings import settings as cfg

class MarsRoverApp(PyQt5.QtWidgets.QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        cfg.SETTINGSEVENT.addListener(self, self.onSettingsChanged)
        self.setWindowIcon(self.loadAppIcon())
        self.loadSettings(cfg.SETTINGS)

    def exec_(self):
        v = super().exec_()
        if v == 0:
            gp.shutdownGamepad()
            udp_conn.disconnectFromRoverServer()

    def onSettingsChanged(self, name, params):
        self.loadSettings(params)

    # Configuration for application, specifically for stylesheet. Dark Mode should overwrite all other settings.
    # TODO: Some texts does not change color in dark mode, specifically the graphs text and logger.
    def loadSettings(self, config):
        darkMode = config.get("main", "stylesheet")
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5()) if darkMode == "True" else self.setStyleSheet("")

    def loadAppIcon(self):
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
    cfg.loadSettings()
    app = MarsRoverApp()
    udp_conn.connectToRoverServer()
    gp.loadGamepad()
    mainwnd = wm.loadMainWindow()
    sys.exit(app.exec_())
