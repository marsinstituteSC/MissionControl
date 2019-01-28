""" Module for the creation of a window to show preferences """

# Normal package imports
import sys
import os
from configparser import ConfigParser

# PyQT5 imports, ignore pylint errors
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QTabWidget
from PyQt5.uic import loadUi

# Package imports
from utils import warning
from camera import window_video as vid

# Default settings
SETTINGS = ConfigParser()

DEFAULT_SECTIONS = ("main", "video")
DEFAULT_MAIN_SETTINGS = {}
DEFAULT_VIDEO_SETTINGS = {
    "url1": "videos/demo.mp4",
    "url2": "videos/demo2.mp4",
    "port1": "",
    "port2": "",
    "color1": "False",
    "color2": "False",
    "resolution1" : 0,
    "resolution2" : 0
}

def loadSettings():
    """
    Loads global settings, creates a new settings.ini file with default
    values if not found.
    """
    global SETTINGS
    try:
        if not os.path.exists("settings.ini"):
            for section in DEFAULT_SECTIONS:
                SETTINGS.add_section(str(section))

            for key, value in DEFAULT_VIDEO_SETTINGS.items():
                SETTINGS.set(str("video"), str(key), str(value))

            with open("settings.ini", "w") as configfile:
                SETTINGS.write(configfile)
        else:
            SETTINGS.read("settings.ini")

        vid.readFromSettings(SETTINGS)
    except:
        warning.showWarning(
            "Fatal Error", "Unable to read/create settings.ini", None)

def saveSettings():
    """
    Save global settings to settings.ini
    """
    global SETTINGS
    try:
        with open("settings.ini", "w") as configfile:
            SETTINGS.write(configfile)

        vid.readFromSettings(SETTINGS)
    except:
        warning.showWarning(
            "Fatal Error", "Unable to write settings.ini", None)

class OptionWindow(QDialog):
    """Window class for settings"""

    def __init__(self):
        super().__init__()
        loadUi("designer/settings.ui", self)

        # Button connections
        self.button_cancel.clicked.connect(self.close)
        self.button_ok.clicked.connect(self.saveSettings)
        self.button_ok.clicked.connect(self.close)
        self.button_apply.clicked.connect(self.saveSettings)

        # Fetch settings
        global SETTINGS

        # Video source and port
        self.video1_ip.setText(SETTINGS.get("video", "url1"))
        self.video2_ip.setText(SETTINGS.get("video", "url2"))
        self.video1_port.setText(SETTINGS.get("video", "port1"))
        self.video2_port.setText(SETTINGS.get("video", "port2"))

        # Color settings
        wantColorForVideo1 = (SETTINGS.get("video", "color1") == "True")
        wantColorForVideo2 = (SETTINGS.get("video", "color2") == "True")
        self.video1_color_on.setChecked(wantColorForVideo1)
        self.video1_color_off.setChecked(not wantColorForVideo1)
        self.video2_color_on.setChecked(wantColorForVideo2)
        self.video2_color_off.setChecked(not wantColorForVideo2)

        # Resolution
        self.video1_resolution.setCurrentIndex(self.video1_resolution.findText(SETTINGS.get("video", "resolution1")))
        self.video2_resolution.setCurrentIndex(self.video2_resolution.findText(SETTINGS.get("video", "resolution2")))

    def saveSettings(self):
        """
        Stores the values into the settings.ini
        Used on apply and OK, for now.
        """
        global SETTINGS

        SETTINGS.set("video", "url1", self.video1_ip.text())
        SETTINGS.set("video", "url2", self.video2_ip.text())
        SETTINGS.set("video", "port1", self.video1_port.text())
        SETTINGS.set("video", "port2", self.video2_port.text())
        SETTINGS.set("video", "color1", str(self.video1_color_on.isChecked()))
        SETTINGS.set("video", "color2", str(self.video2_color_on.isChecked()))
        SETTINGS.set("video", "resolution1", self.video1_resolution.currentText())
        SETTINGS.set("video", "resolution2", self.video2_resolution.currentText())
        saveSettings()

def openSettings():
    settings = OptionWindow()
    settings.show()
    return settings
