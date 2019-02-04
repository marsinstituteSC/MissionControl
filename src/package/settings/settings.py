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
from utils import warning, event
from camera import window_video as vid

SETTINGSEVENT = event.Event("SettingsChangedEvent")

# Default settings
SETTINGS = ConfigParser()
SETTINGSWINDOW = None

DEFAULT_SECTIONS = ("main", "video")
DEFAULT_MAIN_SETTINGS = {
    # Empty means no stylesheet, default look
    "stylesheet" : "False",
    "serverAddress" : "127.0.0.1",
    "serverPort" : "5000",
    "comProtocol" : "UDP"
}
DEFAULT_VIDEO_SETTINGS = {
    "url1": "videos/demo.mp4",
    "url2": "videos/demo2.mp4",
    "port1": "",
    "port2": "",
    "color1": "False",
    "color2": "False",
    "scaling1" : "Source",
    "scaling2" : "Source",
    "resolution1" : 1,
    "resolution2" : 1,
    "name1" : "",
    "name2" : "",
    "enable1" : False,
    "enable2" : False
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
            
            for key, value in DEFAULT_MAIN_SETTINGS.items():
                SETTINGS.set(str("main"), str(key), str(value))

            for key, value in DEFAULT_VIDEO_SETTINGS.items():
                SETTINGS.set(str("video"), str(key), str(value))

            with open("settings.ini", "w") as configfile:
                SETTINGS.write(configfile)
        else:
            SETTINGS.read("settings.ini")
    except:
        warning.showWarning(
            "Fatal Error", "Unable to read/create settings.ini", None)

def saveSettings():
    """
    Save global settings to settings.ini
    """
    global SETTINGS
    global SETTINGSEVENT
    try:
        with open("settings.ini", "w") as configfile:
            SETTINGS.write(configfile)

        SETTINGSEVENT.raiseEvent(SETTINGS)
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
        #self.button_ok.clicked.connect(self.saveSettings)
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
        self.video1_color_on.setChecked((SETTINGS.get("video", "color1") == "True"))
        self.video1_color_off.setChecked(not (SETTINGS.get("video", "color1") == "True"))
        self.video2_color_on.setChecked((SETTINGS.get("video", "color2") == "True"))
        self.video2_color_off.setChecked(not (SETTINGS.get("video", "color2") == "True"))

        # Scaling
        self.video1_scaling.setCurrentIndex(self.video1_scaling.findText(SETTINGS.get("video", "scaling1")))
        self.video2_scaling.setCurrentIndex(self.video2_scaling.findText(SETTINGS.get("video", "scaling2")))

        # Resolution, NOTE this is for camera resolution from rover
        self.video1_resolution.setCurrentIndex(self.video1_resolution.findText("Mode: " + SETTINGS.get("video", "resolution1")))
        self.video2_resolution.setCurrentIndex(self.video2_resolution.findText("Mode: " + SETTINGS.get("video", "resolution2")))

        # Name
        self.video1_name.setText(SETTINGS.get("video", "name1"))
        self.video2_name.setText(SETTINGS.get("video", "name2"))

        # Enable
        self.video1_enable.setChecked((SETTINGS.get("video", "enable1") == "True"))
        self.video2_enable.setChecked((SETTINGS.get("video", "enable2") == "True"))

        # Dark Mode
        self.checkBox_dark.setChecked((SETTINGS.get("main", "stylesheet") == "True"))
        
        # Communication
        self.server_address.setText(SETTINGS.get("main", "serverAddress"))
        self.server_port.setText(SETTINGS.get("main", "serverPort"))
        self.client_address.setText(SETTINGS.get("main", "clientAddress"))
        self.client_port.setText(SETTINGS.get("main", "clientPort"))
        self.radioButton_udp.setChecked((SETTINGS.get("main", "comProtocol") == "True"))
        self.radioButton_tcp.setChecked(not (SETTINGS.get("main", "comProtocol") == "True"))


    def saveSettings(self):
        """
        Stores the values into the settings.ini
        Used on apply.
        """
        global SETTINGS

        # Video
        SETTINGS.set("video", "url1", self.video1_ip.text())
        SETTINGS.set("video", "url2", self.video2_ip.text())
        SETTINGS.set("video", "port1", self.video1_port.text())
        SETTINGS.set("video", "port2", self.video2_port.text())
        SETTINGS.set("video", "color1", str(self.video1_color_on.isChecked()))
        SETTINGS.set("video", "color2", str(self.video2_color_on.isChecked()))
        SETTINGS.set("video", "scaling1", self.video1_scaling.currentText())
        SETTINGS.set("video", "scaling2", self.video2_scaling.currentText())
        SETTINGS.set("video", "name1", self.video1_name.text())
        SETTINGS.set("video", "name2", self.video2_name.text())
        SETTINGS.set("video", "enable1", str(self.video1_enable.isChecked()))
        SETTINGS.set("video", "enable2", str(self.video2_enable.isChecked()))
        
        # Need to check if there has been a change to the resolution, if so it needs to send that info to the rover
        oldRes1 = SETTINGS.get("video", "resolution1")
        oldRes2 = SETTINGS.get("video", "resolution2")
        newRes1 = self.video1_resolution.currentText().split(": ")[1]
        newRes2 = self.video2_resolution.currentText().split(": ")[1]
        if oldRes1 != newRes1:
            SETTINGS.set("video", "resolution1", newRes1)
            updateResolutionOnCamera(SETTINGS.get("video", "name1"), newRes1)
        if oldRes2 != newRes2:
            SETTINGS.set("video", "resolution2", newRes2)
            updateResolutionOnCamera(SETTINGS.get("video", "name2"), newRes2)
        
        # Main
        SETTINGS.set("main", "stylesheet", str(self.checkBox_dark.isChecked()))
        SETTINGS.set("main", "serverAddress", str(self.server_address.text()))
        SETTINGS.set("main", "serverPort", str(self.server_port.text()))
        SETTINGS.set("main", "clientAddress", str(self.client_address.text()))
        SETTINGS.set("main", "clientPort", str(self.client_port.text()))
        SETTINGS.set("main", "comProtocol", str(self.radioButton_udp.isChecked()))
        saveSettings()

    def closeEvent(self, event):
        global SETTINGSWINDOW
        SETTINGSWINDOW = None

def updateResolutionOnCamera(name, mode):
    """
    Creates and sends an update to the rover with the new resoltion
    Inputs:
        Name: The name of the camera, needs to be the same as the one on the rover
        Mode: Arbitrary mode ranging from 1-4 to change resolution
    """
    # This will change to the json specification
    output = {
        "cameraName" : name,
        "cameraMode" : mode
    }
    # Send to udp, will do this later.


def openSettings():
    """Open global settings"""
    global SETTINGSWINDOW
    if SETTINGSWINDOW is None:
        SETTINGSWINDOW = OptionWindow()

    SETTINGSWINDOW.show()
    SETTINGSWINDOW.activateWindow()
    return SETTINGSWINDOW