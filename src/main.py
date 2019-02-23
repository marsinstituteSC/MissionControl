""" Default Application Entry Point """

import sys
import qdarkstyle
import cProfile
import time

from PyQt5.QtWidgets import QSystemTrayIcon, QApplication, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

from communications import udp_conn, database
from controller import gamepad as gp
from mainwindow import window_main as wm
from utils import event
from settings import settings as cfg

APP_RESTART_CODE = -2500

class MarsRoverApp(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        cfg.SETTINGSEVENT.addListener(self, self.onSettingsChanged)
        cfg.RESTARTEVENT.addListener(self, self.onCheckShouldRestart)
        self.setWindowIcon(self.loadAppIcon())
        self.loadSettings(cfg.SETTINGS)

    def exec_(self):
        v = super().exec_() # Returns 'return code'...
        gp.shutdownGamepad()
        udp_conn.disconnectFromRoverServer()
        return v

    def onSettingsChanged(self, name, params):
        self.loadSettings(params)

    def onCheckShouldRestart(self, name, params):
        """
        Triggered by the settings GUI, params = settings GUI window class.
        """
        msg = QMessageBox(QMessageBox.Warning, "Restart Required!",
                          "The application has to be restarted in order to apply the desired changes, would you like to restart now?",
                          QMessageBox.Yes | QMessageBox.No)
        if msg.exec_() == QMessageBox.Yes:
            params.saveSettings()  # Save state first.
            params.close()
            self.exit(APP_RESTART_CODE)

    # Configuration for application, specifically for stylesheet. Dark Mode should overwrite all other settings.
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

    code = APP_RESTART_CODE
    cfg.loadSettings()    
    while code == APP_RESTART_CODE:
        database.loadDatabase()
        app = MarsRoverApp()
        udp_conn.connectToRoverServer()
        gp.loadGamepad()
        mainwnd = wm.loadMainWindow()
        code = app.exec_()
        mainwnd.close()
        app = None
        mainwnd = None
        if code == APP_RESTART_CODE:
            cfg.SETTINGSEVENT.clearListeners()
            cfg.RESTARTEVENT.clearListeners()
            print("Restarting App!")
            time.sleep(1 / 2)            
    sys.exit(code)
