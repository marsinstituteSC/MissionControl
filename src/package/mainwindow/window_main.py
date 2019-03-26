""" Main App Window, renders information from sensors, render graphs, etc... """

import random
import time
import datetime
import cProfile

from PyQt5.QtWidgets import QMainWindow, QWidget, QTabWidget, QLCDNumber, QHBoxLayout, QLabel, QGridLayout, QPushButton, QComboBox, QDateTimeEdit, QLineEdit, QCheckBox, QSpacerItem, QSizePolicy
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QDateTime

from widgets import plot
from widgets import logger
from communications import udp_conn
from camera import window_video as wv
from settings import settings as cfg
from mainwindow import window_eventlog
from controller import gamepad as gp
from widgets.gyroscope import GyroscopeWidget
from widgets.simpleStatus import SimpleStatus
from widgets.compass import CompassWidget
from widgets.motionControl import MotionControlWidget
from widgets.battery import BatteryWidget
from widgets.controlStationStatus import ControlStatus
from widgets.speed import SpeedWidget
from widgets.message import CustomMessageWidget

from utils.warning import showWarning
from communications import database

def getValueForDBEvent(e):
    try:
        return float(e.message)
    except:
        return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("designer/window_main.ui", self)
        self.setWindowTitle("JARL Viking III")    
        self.setupUi()

        # Creates the video window as a child and links a button to open it later
        self.video_window = None
        self.actionCamera.triggered.connect(self.openCameraWindow)

        # Toolbar button to open settings
        self.actionSettings.triggered.connect(self.settings)
        self.actionLog.triggered.connect(window_eventlog.showEventLog)

        # Gamepad toolbar
        self.gamepadRefresh.triggered.connect(self.refreshGamepad)
        self.menuGamepads.triggered.connect(self.initializeGamepad)        
        gp.GAMEPAD.refreshedGamepad.connect(self.populateGamepads)
        gp.GAMEPAD.statusChanged.connect(self.changeGamepadStatus)
        self.refreshGamepad() # Re-init + fetch list of gamepads

        database.SIGNAL.status.connect(self.changeDatabaseStatus)
        udp_conn.ROVERSERVER.communicationTimeout.connect(self.changeRoverStatus)

        udp_conn.ROVERSERVER.onReceiveData.connect(self.receivedDataFromRover)        

    def setupUi(self):
        """
        Load/Create UI controls, the toolbar has been created via the UI file.
        """
        # Assign logger to group box in grid.
        self.log = logger.ColorizedLogger()
        self.log.logData("Anything, especially stuff we normally don't care about", logger.LOGGER_PRIORITY_COMMON)
        self.log.logData("Something normal happened", logger.LOGGER_PRIORITY_NOTIFICATION)
        self.log.logData("Something might be wrong", logger.LOGGER_PRIORITY_WARNING) 
        self.log.logData("Something is definitely wrong", logger.LOGGER_PRIORITY_ERROR)
        self.logSection.layout().addWidget(self.log)

        self.gyro = GyroscopeWidget()
        self.status = SimpleStatus()
        self.compass = CompassWidget()
        self.motionControl = MotionControlWidget()
        self.battery = BatteryWidget()
        self.controlStatus = ControlStatus()
        self.speed = SpeedWidget()
        self.message = CustomMessageWidget()
        self.leftFrameGrid.addWidget(self.controlStatus, 0, 0)
        self.leftFrameGrid.addWidget(self.status, 1, 0)
        self.topFrameGrid.addWidget(self.compass, 0, 0)
        self.topFrameGrid.addWidget(self.gyro, 1, 0)
        self.bottomFrameGrid.addWidget(self.speed, 0, 0)
        self.bottomFrameGrid.addWidget(self.battery, 0, 1)
        self.rightFrameGrid.addWidget(self.message, 1, 0)  
        self.rightFrameGrid.addWidget(self.motionControl, 2, 0)

        # Make 1 row, 1 columns, 1 plot
        self.graph = plot.PlotCanvas(None, 10)        
        self.gridPlotting.addWidget(self.graph, 0, 0)

        self.frameGraphSettings.findChild(QPushButton, "btnPlotter").clicked.connect(self.plotGraph)
        # Use current date for date pickers by def.
        self.frameGraphSettings.findChild(QDateTimeEdit, "plotTimeStart").setDateTime(QDateTime.currentDateTime())
        self.frameGraphSettings.findChild(QDateTimeEdit, "plotTimeEnd").setDateTime(QDateTime.currentDateTime())

        self.splitter.setStyleSheet("QSplitter::handle:horisontal {\n"
        "border-width: 0px 0px 2px 0px;\n"
        "border-style: dotted;\n"
        "border-color: grey;\n"
        "}")
        self.status.testWidget()

    def closeEvent(self, event):
        super().closeEvent(event)
        if self.video_window:
            self.video_window.close()
            
        self.video_window = None

    def refreshGamepad(self):
        # Sets the refresh boolean to true for the gamepad class to check for new gamepads in the new iteration.
        gp.GAMEPAD.needRefresh = True

    def populateGamepads(self, joyDict):
        self.menuGamepads.clear()
        for id, name in joyDict.items():
            self.menuGamepads.addAction(str(id) + ": " + str(name))

    def initializeGamepad(self, gamepad):
        id, _ = gamepad.text().split(": ")
        gp.GAMEPAD.joystick_id_switch = int(id)
    
    def changeGamepadStatus(self, status):
        self.controlStatus.setControllerStatus(status)

    def changeRoverStatus(self, status):
        self.controlStatus.setRoverStatus(status)

    def changeDatabaseStatus(self, status):
        self.controlStatus.setDatabaseStatus(status[0])
        if not status[0]: # Print error.
            self.log.logData(str(status[1]), logger.LOGGER_PRIORITY_ERROR)

    def setSpeedometerValue(self, value):
        self.speed.setSpeed(value)

    def settings(self):
        self.setting = cfg.openSettings()
    
    def openCameraWindow(self):
        if self.video_window is None:
            self.video_window = wv.loadCameraWindow()
        elif self.video_window.isHidden():
            self.video_window.show()
        else:
            self.video_window.setWindowState(Qt.WindowActive)

        self.video_window.activateWindow()

    def plotGraph(self):
        try:
            selectedType = self.frameGraphSettings.findChild(QComboBox, "plotDataType").currentIndex()
            startDate = datetime.datetime.fromtimestamp(self.frameGraphSettings.findChild(QDateTimeEdit, "plotTimeStart").dateTime().toMSecsSinceEpoch() / 1000)
            endDate = datetime.datetime.fromtimestamp(self.frameGraphSettings.findChild(QDateTimeEdit, "plotTimeEnd").dateTime().toMSecsSinceEpoch() / 1000)
            minValue = float(self.frameGraphSettings.findChild(QLineEdit, "fieldMinVal").text())
            maxValue = float(self.frameGraphSettings.findChild(QLineEdit, "fieldMaxVal").text())
            useValueRange = self.frameGraphSettings.findChild(QCheckBox, "plotCheckMinMax").isChecked()

            data = database.Event.findTypeWithin(selectedType, startDate, endDate, True)
            if len(data) <= 0:
                showWarning("Error!", "No data available for the selected type or within the selected timespan!", self)
                return

            # Filter out 'broken' values.
            values = list()
            for d in data:
                v = getValueForDBEvent(d)
                if v:
                    if useValueRange and not (v >= minValue and v <= maxValue):
                        continue

                    values.append(v)

            self.graph.clearGraph()
            self.graph.plot("", values, 111)
        except:
            showWarning("Error!", "Invalid input(s) inserted!", self)

    @pyqtSlot('PyQt_PyObject')
    def receivedDataFromRover(self, data):
        """
        When a packet arrives from the rover, an event is triggered, the event is sent safely to the Qt GUI thread, the incoming data is a json
        object, which can be parsed properly in this method.
        """
        # TODO Add more stuff here...
        if 'speed' in data:
            self.setSpeedometerValue(data['speed'])
            self.log.logData("Speed {} m/s.".format(data['speed']), logger.LOGGER_PRIORITY_NOTIFICATION, logger.LOGGER_TYPE_ROVER)

def loadMainWindow():
    wndw = MainWindow()
    wndw.showMaximized()
    wndw.openCameraWindow()
    return wndw