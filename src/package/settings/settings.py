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
from communications import database
from communications import udp_conn as UDP

SETTINGSEVENT = event.Event("SettingsChangedEvent")
RESTARTEVENT = event.Event("RestartAppEvent")

# Default settings
SETTINGS = ConfigParser()
SETTINGSWINDOW = None

DEFAULT_SECTIONS = ("main", "database", "communication")
DEFAULT_MAIN_SETTINGS = {
    # Empty means no stylesheet, default look
    "stylesheet" : "False",
    "multithread" : "False"
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

            for key, value in DEFAULT_DATABASE_SETTINGS.items():
                SETTINGS.set(str("database"), str(key), str(value))

            for key, value in DEFAULT_COMMUNICATION_SETTINGS.items():
                SETTINGS.set(str("communication"), str(key), str(value))

            with open("settings.ini", "w") as configfile:
                SETTINGS.write(configfile)
        else:
            SETTINGS.read("settings.ini")
    except:
        warning.showWarning("Fatal Error", "Unable to read/create settings.ini", None)

def saveSettings():
    """
    Save global settings to settings.ini
    """
    global SETTINGS, SETTINGSEVENT
    try:
        with open("settings.ini", "w") as configfile:
            SETTINGS.write(configfile)

        SETTINGSEVENT.raiseEvent(SETTINGS)
    except Exception as e:
        warning.showWarning("Fatal Error", "Unable to write settings.ini", None)

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
        self.button_dbCreateDB.clicked.connect(self.createDatabase)

        # Fetch settings
        global SETTINGS

        # Dark Mode
        self.checkBox_dark.setChecked((SETTINGS.get("main", "stylesheet") == "True"))

        # Threadmode - Multi threaded camera streams or synced on a single unique thread.
        self.threadSync.setChecked(not (SETTINGS.get("main", "multithread") == "True"))
        self.threadAsync.setChecked((SETTINGS.get("main", "multithread") == "True"))

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

        # Warning        
        self.threadAsync.toggled.connect(lambda: RESTARTEVENT.raiseEvent(self))

    def saveSettings(self):
        """
        Stores the values into the settings.ini
        Used on apply.
        """
        global SETTINGS

        # Main
        SETTINGS.set("main", "stylesheet", str(self.checkBox_dark.isChecked()))
        SETTINGS.set("main", "multithread", str(not self.threadSync.isChecked()))

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
            database.deleteDataFromDatabase()

    def createDatabase(self):
        if warning.showPrompt("Disclaimer!", "Create a new database? You may have to restart the program!", self) == QMessageBox.Yes:
            try:
                database.createDatabase(self.databaseDB.text())
            except Exception as e:
                warning.showWarning("Error!", str(e), self)

def openSettings():
    """Open global settings"""
    global SETTINGSWINDOW
    if SETTINGSWINDOW is None:
        SETTINGSWINDOW = OptionWindow()

    SETTINGSWINDOW.show()
    SETTINGSWINDOW.activateWindow()
    return SETTINGSWINDOW