""" Default Application Entry Point """

import sys
import qdarkstyle
import cProfile

from PyQt5.QtWidgets import QSystemTrayIcon, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

from communications import udp_conn, database
from controller import gamepad as gp
from mainwindow import window_main as wm
from utils import event
from settings import settings as cfg


class MarsRoverApp(QApplication):
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
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5(
        )) if darkMode == "True" else self.setStyleSheet("")

    def loadAppIcon(self):
        """Load application default icon, for all windows + taskbar"""
        app_icon = QIcon()
        app_icon.addFile('images/logo_16.png', QSize(16, 16))
        app_icon.addFile('images/logo_24.png', QSize(24, 24))
        app_icon.addFile('images/logo_32.png', QSize(32, 32))
        app_icon.addFile('images/logo_48.png', QSize(48, 48))
        app_icon.addFile('images/logo_256.png', QSize(256, 256))
        app_icon.addFile('images/logo.png', QSize(512, 512))
        return app_icon


if __name__ == "__main__":
    #pr = cProfile.Profile()
    #pr.enable()
    #pr.disable()
    #pr.print_stats(sort='time')
    cfg.loadSettings()
    database.loadDatabase()
    app = MarsRoverApp()
    udp_conn.connectToRoverServer()
    gp.loadGamepad()
    mainwnd = wm.loadMainWindow()
    sys.exit(app.exec_())
