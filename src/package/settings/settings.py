"""Module for the creation of a window to show preferences"""

# Normal package imports
import sys
from configparser import ConfigParser

# PyQT5 imports, ignore pylint errors
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QTabWidget
from PyQt5.uic import loadUi


class OptionWindow(QDialog):
    """Window class for settings"""
    def __init__(self):
        super(OptionWindow, self).__init__()
        loadUi("src/designer/settings.ui", self)

        # Button connections
        self.button_cancel.clicked.connect(self.closeSelf)
        self.button_ok.clicked.connect(self.saveSettings)
        self.button_ok.clicked.connect(self.closeSelf)
        self.button_apply.clicked.connect(self.saveSettings)

        # Read from settings.ini to polulate the current settings
        config = ConfigParser()
        config.read("src/settings.ini")
        self.video1_ip.setText(config.get("video", "url1"))
        self.video2_ip.setText(config.get("video", "url2"))
        self.video1_port.setText(config.get("video", "port1"))
        self.video2_port.setText(config.get("video", "port2"))
        if config.get("video", "color1") == "True":
            self.video1_color_on.setChecked(True)
            self.video1_color_off.setChecked(False)
        else:
            self.video1_color_off.setChecked(True)
            self.video1_color_on.setChecked(False)

        if config.get("video", "color2") == "True":
            self.video2_color_on.setChecked(True)
            self.video2_color_off.setChecked(False)
        else:
            self.video2_color_off.setChecked(True)
            self.video2_color_on.setChecked(False)

    def closeSelf(self):
        """
        Closes the dialog window without closing the whole program
        """
        self.close()

    def saveSettings(self):
        """
        Stores the values into the settings.ini
        Used on apply and OK, for now.
        """

        # Open settings.ini file and write to it
        config = ConfigParser()
        config.read("src/settings.ini")
        config.set("video", "url1", self.video1_ip.text())
        config.set("video", "url2", self.video2_ip.text())
        config.set("video", "port1", self.video1_port.text())
        config.set("video", "port2", self.video2_port.text())
        config.set("video", "color1", str(self.video1_color_on.isChecked()))
        config.set("video", "color2", str(self.video2_color_on.isChecked()))
        with open("src/settings.ini", "w") as configfile:
            config.write(configfile)

def openSettings():
    settings = OptionWindow()
    settings.show()
    return settings


if __name__ == "__main__":
    APP = QApplication(sys.argv)
    WINDOW = OptionWindow()
    WINDOW.show()
    sys.exit(APP.exec_())
