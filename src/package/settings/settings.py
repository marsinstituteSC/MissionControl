""" Module for the creation of a window to show preferences """

# Normal package imports
import sys, os
from configparser import ConfigParser

# PyQT5 imports, ignore pylint errors
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QTabWidget
from PyQt5.uic import loadUi

# Package imports
from utils import warning
from camera import window_video as vid

# Default settings
DEFAULT_SECTIONS = ("main", "video")
DEFAULT_MAIN_SETTINGS = {}
DEFAULT_VIDEO_SETTINGS = {
    "url1" : "videos/demo.mp4",
    "url2" : "videos/demo2.mp4",
    "port1" : "",
    "port2" : "",
    "color1" : "False",
    "color2" : "False"
}

class OptionWindow(QDialog):
    """Window class for settings"""
    def __init__(self):
        super().__init__()
        loadUi("designer/settings.ui", self)

        # Button connections
        self.button_cancel.clicked.connect(self.closeSelf)
        self.button_ok.clicked.connect(self.saveSettings)
        self.button_ok.clicked.connect(self.closeSelf)
        self.button_apply.clicked.connect(self.saveSettings)

        # Read from settings.ini to polulate the current settings
        try:
            config = ConfigParser()
            config.read("settings.ini")
            self.video1_ip.setText(config.get("video", "url1"))
            self.video2_ip.setText(config.get("video", "url2"))
            self.video1_port.setText(config.get("video", "port1"))
            self.video2_port.setText(config.get("video", "port2"))

            wantColorForVideo1 = (config.get("video", "color1") == "True")
            wantColorForVideo2 = (config.get("video", "color2") == "True")

            self.video1_color_on.setChecked(wantColorForVideo1)
            self.video1_color_off.setChecked(not wantColorForVideo1)

            self.video2_color_on.setChecked(wantColorForVideo2)
            self.video2_color_off.setChecked(not wantColorForVideo2)
        except:
            warning.ShowWarning(self, "Fatal Error", "Unable to read settings.ini")

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
        try:
            config = ConfigParser()
            config.read("settings.ini")
            config.set("video", "url1", self.video1_ip.text())
            config.set("video", "url2", self.video2_ip.text())
            config.set("video", "port1", self.video1_port.text())
            config.set("video", "port2", self.video2_port.text())
            config.set("video", "color1", str(self.video1_color_on.isChecked()))
            config.set("video", "color2", str(self.video2_color_on.isChecked()))
            with open("settings.ini", "w") as configfile:
                config.write(configfile)
        except:
            warning.ShowWarning(self, "Fatal Error", "Unable to read & write settings.ini")

        # Runs functions to update variables for the other windows, currently only video
        vid.readFromSettings()

def checkSettings():
    """
    Checks if settings.ini has been created
    if it is missing create one with default values
    """
    if not os.path.exists("settings.ini"):
        try:
            config = ConfigParser()
            config.read("settings.ini")
            for section in DEFAULT_SECTIONS:
                config.add_section(str(section))
            
            for key, value in DEFAULT_VIDEO_SETTINGS.items():
                config.set(str("video"), str(key), str(value))
            
            with open("settings.ini", "w") as configfile:
                config.write(configfile)
        except:
            print("ERROR WITH CREATING A NEW SETTINGS FILE")

def openSettings():
    settings = OptionWindow()
    settings.show()
    return settings