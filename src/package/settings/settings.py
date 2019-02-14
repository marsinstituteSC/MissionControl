""" Module for the creation of a window to show preferences """

# Normal package imports
import sys
import os
from configparser import ConfigParser
import json

# PyQT5 imports, ignore pylint errors
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QTabWidget, QMessageBox
from PyQt5.uic import loadUi

# Package imports
from utils import warning, event
from camera import window_video as vid
from communications import database
from communications import udp_conn as UDP

SETTINGSEVENT = event.Event("SettingsChangedEvent")

# Default settings
SETTINGS = ConfigParser()
SETTINGSWINDOW = None

DEFAULT_SECTIONS = ("main", "video", "database", "communication")
DEFAULT_MAIN_SETTINGS = {
    # Empty means no stylesheet, default look
    "stylesheet" : "False"
}
DEFAULT_VIDEO_SETTINGS = {
    "url1": "videos/demo.mp4",
    "url2": "videos/demo2.mp4",
    "url3" : "",
    "url4" : "",
    "port1": "",
    "port2": "",
    "port3": "",
    "port4": "",
    "color1": "False",
    "color2": "False",
    "color3": "False",
    "color4": "False",
    "scaling1" : "Source",
    "scaling2" : "Source",
    "scaling3" : "Source",
    "scaling4" : "Source",
    "resolution1" : 1,
    "resolution2" : 1,
    "resolution3" : 1,
    "resolution4" : 1,
    "name1" : "Video1",
    "name2" : "Video2",
    "name3" : "Video3",
    "name4" : "Video4",
    "enable1" : True,
    "enable2" : True,
    "enable3" : True,
    "enable4" : True
}
DEFAULT_DATABASE_SETTINGS = {
    "address": "127.0.0.1",
    "port": 5432,
    "db": "rover",
    "user": "postgres",
    "passwd": "xyz",
    "type": "postgresql"
}
DEFAULT_COMMUNICATION_SETTINGS = {
    "serverGamepadAddress" : "127.0.0.1",
    "serverGamepadPort" : "5000",
    "clientGamepadAddress" : "127.0.0.1",
    "clientGamepadPort" : "37500",
    "comGamepadProtocol" : "True", # True - UDP, TCP otherwise.
    "serverRoverAddress" : "239.255.43.21", # Rover Broadcast Addr.
    "serverRoverPort" : "45454"
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

            for key, value in DEFAULT_DATABASE_SETTINGS.items():
                SETTINGS.set(str("database"), str(key), str(value))

            for key, value in DEFAULT_COMMUNICATION_SETTINGS.items():
                SETTINGS.set(str("communication"), str(key), str(value))

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
        self.properties_tab.setCurrentIndex(0)

        # Button connections
        self.button_cancel.clicked.connect(self.close)
        #self.button_ok.clicked.connect(self.saveSettings)
        self.button_ok.clicked.connect(self.close)
        self.button_apply.clicked.connect(self.saveSettings)
        self.button_dbDropAll.clicked.connect(self.dropDatabaseTable)

        # Fetch settings
        global SETTINGS

        # Video source and port
        self.video1_ip.setText(SETTINGS.get("video", "url1"))
        self.video2_ip.setText(SETTINGS.get("video", "url2"))
        self.video3_ip.setText(SETTINGS.get("video", "url3"))
        self.video4_ip.setText(SETTINGS.get("video", "url4"))
        self.video1_port.setText(SETTINGS.get("video", "port1"))
        self.video2_port.setText(SETTINGS.get("video", "port2"))
        self.video3_port.setText(SETTINGS.get("video", "port3"))
        self.video4_port.setText(SETTINGS.get("video", "port4"))

        # Color settings
        self.video1_color_on.setChecked((SETTINGS.get("video", "color1") == "True"))
        self.video1_color_off.setChecked(not (SETTINGS.get("video", "color1") == "True"))
        self.video2_color_on.setChecked((SETTINGS.get("video", "color2") == "True"))
        self.video2_color_off.setChecked(not (SETTINGS.get("video", "color2") == "True"))
        self.video3_color_on.setChecked((SETTINGS.get("video", "color3") == "True"))
        self.video3_color_off.setChecked(not (SETTINGS.get("video", "color3") == "True"))
        self.video4_color_on.setChecked((SETTINGS.get("video", "color4") == "True"))
        self.video4_color_off.setChecked(not (SETTINGS.get("video", "color4") == "True"))

        # Scaling
        self.video1_scaling.setCurrentIndex(self.video1_scaling.findText(SETTINGS.get("video", "scaling1")))
        self.video2_scaling.setCurrentIndex(self.video2_scaling.findText(SETTINGS.get("video", "scaling2")))
        self.video3_scaling.setCurrentIndex(self.video3_scaling.findText(SETTINGS.get("video", "scaling3")))
        self.video4_scaling.setCurrentIndex(self.video4_scaling.findText(SETTINGS.get("video", "scaling4")))

        # Resolution, NOTE this is for camera resolution from rover
        self.video1_resolution.setCurrentIndex(self.video1_resolution.findText("Mode: " + SETTINGS.get("video", "resolution1")))
        self.video2_resolution.setCurrentIndex(self.video2_resolution.findText("Mode: " + SETTINGS.get("video", "resolution2")))
        self.video3_resolution.setCurrentIndex(self.video3_resolution.findText("Mode: " + SETTINGS.get("video", "resolution3")))
        self.video4_resolution.setCurrentIndex(self.video4_resolution.findText("Mode: " + SETTINGS.get("video", "resolution4")))

        # Name
        self.video1_name.setText(SETTINGS.get("video", "name1"))
        self.video2_name.setText(SETTINGS.get("video", "name2"))
        self.video3_name.setText(SETTINGS.get("video", "name3"))
        self.video4_name.setText(SETTINGS.get("video", "name4"))

        # Enable
        self.video1_enable.setChecked((SETTINGS.get("video", "enable1") == "True"))
        self.video2_enable.setChecked((SETTINGS.get("video", "enable2") == "True"))
        self.video3_enable.setChecked((SETTINGS.get("video", "enable3") == "True"))
        self.video4_enable.setChecked((SETTINGS.get("video", "enable4") == "True"))

        # Dark Mode
        self.checkBox_dark.setChecked((SETTINGS.get("main", "stylesheet") == "True"))

        # Database
        self.databaseAddress.setText(SETTINGS.get("database", "address"))
        self.databasePort.setText(SETTINGS.get("database", "port"))
        self.databaseDB.setText(SETTINGS.get("database", "db"))
        self.databaseUser.setText(SETTINGS.get("database", "user"))
        self.databasePassword.setText(SETTINGS.get("database", "passwd"))
        self.checkMySQL.setChecked(True) if (SETTINGS.get("database", "type") == "mysql") else self.checkPostgreSQL.setChecked(True)

        self.checkMySQL.toggled.connect(self.setDefaultDBPort)
        self.checkPostgreSQL.toggled.connect(self.setDefaultDBPort)

        # Communication
        self.server_address.setText(SETTINGS.get("communication", "serverGamepadAddress"))
        self.server_port.setText(SETTINGS.get("communication", "serverGamepadPort"))
        self.client_address.setText(SETTINGS.get("communication", "clientGamepadAddress"))
        self.client_port.setText(SETTINGS.get("communication", "clientGamepadPort"))
        self.radioButton_udp.setChecked((SETTINGS.get("communication", "comGamepadProtocol") == "True"))
        self.radioButton_tcp.setChecked(not (SETTINGS.get("communication", "comGamepadProtocol") == "True"))   
        self.rover_address.setText(SETTINGS.get("communication", "serverRoverAddress"))
        self.rover_port.setText(SETTINGS.get("communication", "serverRoverPort"))   

    def saveSettings(self):
        """
        Stores the values into the settings.ini
        Used on apply.
        """
        global SETTINGS

        # Video
        SETTINGS.set("video", "url1", self.video1_ip.text())
        SETTINGS.set("video", "url2", self.video2_ip.text())
        SETTINGS.set("video", "url3", self.video3_ip.text())
        SETTINGS.set("video", "url4", self.video4_ip.text())
        SETTINGS.set("video", "port1", self.video1_port.text())
        SETTINGS.set("video", "port2", self.video2_port.text())
        SETTINGS.set("video", "port3", self.video3_port.text())
        SETTINGS.set("video", "port4", self.video4_port.text())
        SETTINGS.set("video", "color1", str(self.video1_color_on.isChecked()))
        SETTINGS.set("video", "color2", str(self.video2_color_on.isChecked()))
        SETTINGS.set("video", "color3", str(self.video3_color_on.isChecked()))
        SETTINGS.set("video", "color4", str(self.video4_color_on.isChecked()))
        SETTINGS.set("video", "scaling1", self.video1_scaling.currentText())
        SETTINGS.set("video", "scaling2", self.video2_scaling.currentText())
        SETTINGS.set("video", "scaling3", self.video3_scaling.currentText())
        SETTINGS.set("video", "scaling4", self.video4_scaling.currentText())
        SETTINGS.set("video", "name1", self.video1_name.text())
        SETTINGS.set("video", "name2", self.video2_name.text())
        SETTINGS.set("video", "name3", self.video3_name.text())
        SETTINGS.set("video", "name4", self.video4_name.text())
        SETTINGS.set("video", "enable1", str(self.video1_enable.isChecked()))
        SETTINGS.set("video", "enable2", str(self.video2_enable.isChecked()))
        SETTINGS.set("video", "enable3", str(self.video3_enable.isChecked()))
        SETTINGS.set("video", "enable4", str(self.video4_enable.isChecked()))
        
        # Need to check if there has been a change to the resolution, if so it needs to send that info to the rover
        oldRes1 = SETTINGS.get("video", "resolution1")
        oldRes2 = SETTINGS.get("video", "resolution2")
        oldRes3 = SETTINGS.get("video", "resolution3")
        oldRes4 = SETTINGS.get("video", "resolution4")
        newRes1 = self.video1_resolution.currentText().split(": ")[1]
        newRes2 = self.video2_resolution.currentText().split(": ")[1]
        newRes3 = self.video3_resolution.currentText().split(": ")[1]
        newRes4 = self.video4_resolution.currentText().split(": ")[1]
        if oldRes1 != newRes1:
            SETTINGS.set("video", "resolution1", newRes1)
            updateResolutionOnCamera(SETTINGS.get("video", "name1"), newRes1)
        if oldRes2 != newRes2:
            SETTINGS.set("video", "resolution2", newRes2)
            updateResolutionOnCamera(SETTINGS.get("video", "name2"), newRes2)
        if oldRes3 != newRes3:
            SETTINGS.set("video", "resolution3", newRes3)
            updateResolutionOnCamera(SETTINGS.get("video", "name3"), newRes3)
        if oldRes4 != newRes4:
            SETTINGS.set("video", "resolution4", newRes4)
            updateResolutionOnCamera(SETTINGS.get("video", "name4"), newRes4)
        
        # Main
        SETTINGS.set("main", "stylesheet", str(self.checkBox_dark.isChecked()))

        # Database
        SETTINGS.set("database", "address", str(self.databaseAddress.text()))
        SETTINGS.set("database", "port", str(self.databasePort.text()))
        SETTINGS.set("database", "db", str(self.databaseDB.text()))
        SETTINGS.set("database", "user", str(self.databaseUser.text()))
        SETTINGS.set("database", "passwd", str(self.databasePassword.text()))
        SETTINGS.set("database", "type", "mysql" if self.checkMySQL.isChecked() else "postgresql")

        # Communication
        SETTINGS.set("communication", "serverGamepadAddress", str(self.server_address.text()))
        SETTINGS.set("communication", "serverGamepadPort", str(self.server_port.text()))
        SETTINGS.set("communication", "clientGamepadAddress", str(self.client_address.text()))
        SETTINGS.set("communication", "clientGamepadPort", str(self.client_port.text()))
        SETTINGS.set("communication", "comGamepadProtocol", str(self.radioButton_udp.isChecked()))
        SETTINGS.set("communication", "serverRoverAddress", str(self.rover_address.text()))
        SETTINGS.set("communication", "serverRoverPort", str(self.rover_port.text()))

        saveSettings()

    def setDefaultDBPort(self):
        self.databasePort.setText("3306") if self.checkMySQL.isChecked() else self.databasePort.setText("5432")
        
    def closeEvent(self, event):
        super().closeEvent(event)
        global SETTINGSWINDOW
        SETTINGSWINDOW = None

    def dropDatabaseTable(self):
        if warning.showPrompt("Disclaimer!", "This will delete all the data from the database, the structure will still be in tact. Do you want to proceed?", self) == QMessageBox.Yes:
            database.deleteDataFromDatabase("sensor")

def updateResolutionOnCamera(name, mode):
    """
    Creates and sends an update to the rover with the new resoltion
    Inputs:
        Name: The name of the camera, needs to be the same as the one on the rover
        Mode: Arbitrary mode ranging from 1-4 to change resolution
    """
    # This will change to the json specification
    msg = {
            "cameraName" : name,
            "cameraMode" : mode
        }
    message = {
        "Camera" : msg
    }
    # Send to udp
    UDP.ROVERSERVER.writeToRover(json.dumps(message, separators=(',', ':')))

def openSettings():
    """Open global settings"""
    global SETTINGSWINDOW
    if SETTINGSWINDOW is None:
        SETTINGSWINDOW = OptionWindow()

    SETTINGSWINDOW.show()
    SETTINGSWINDOW.activateWindow()
    return SETTINGSWINDOW