""" Main App Window, renders information from sensors, render graphs, etc... """

import random, time
import cProfile

from PyQt5.QtWidgets import QMainWindow, QWidget, QTabWidget, QLCDNumber, QHBoxLayout, QLabel, QGridLayout
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

from controls import plot
from controls import logger
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("designer/window_main.ui", self)
        self.setWindowTitle("JARL Viking III")    
        self.setupUi()

        # Creates the video window as a child and links a button to open it later
        self.video_window = None
        #self.openCameraWindow()
        self.actionCamera_Window.triggered.connect(self.openCameraWindow)

        # Toolbar button to open settings
        self.actionSettings.triggered.connect(self.settings)
        self.actionLog.triggered.connect(window_eventlog.showEventLog)

        # Gamepad toolbar
        self.gamepadRefresh.triggered.connect(self.refreshGamepad)
        self.menuGamepads.triggered.connect(self.initializeGamepad)
        self.refreshGamepad()
        self.populateGamepads()

        udp_conn.ROVERSERVER.onReceiveData.connect(self.receivedDataFromRover)

    def setupUi(self):
        """
        Load/Create UI controls, the toolbar has been created via the UI file.
        """
        # Assign logger to group box in grid.
        self.log = logger.ColorizedLogger()
        self.log.logData("Anything, especially stuff we normally don't care about", 0)
        self.log.logData("Something normal happened", 1)
        self.log.logData("Something might be wrong", 2) 
        self.log.logData("Something is definitely wrong", 3)
        self.logSection.layout().addWidget(self.log)

        # Assign measurement displays to the status TAB.
        #statusTAB = self.tabSection.widget(0)
        #statusTAB.layout().addStretch()

        #self.speedMeter = QLCDNumber()
        #self.speedMeter.setSegmentStyle(QLCDNumber.Flat)
        self.gyro = GyroscopeWidget()
        self.status = SimpleStatus()
        self.compass = CompassWidget()
        self.motionControl = MotionControlWidget()
        self.battery = BatteryWidget()
        self.leftFrameGrid.addWidget(self.status, 0, 0)
        self.topFrameGrid.addWidget(self.compass, 0, 0)
        self.bottomFrameGrid.addWidget(self.gyro, 0, 0)
        self.bottomFrameGrid.addWidget(self.battery, 0, 1)
        self.rightFrameGrid.addWidget(self.motionControl, 0, 0)

        # NOTE: Commented this out since it will be contained in its own widget
        #self.horizontalLayout.addWidget(QLabel("Speed"))
        #self.horizontalLayout.addWidget(self.speedMeter)
        #self.horizontalLayout.addWidget(QLabel("m/s"))
        #self.setSpeedometerValue(12)           

        # Make 1 row, 2 columns, 2 plots
        graphs1 = plot.PlotCanvas(None, 10)        
        graphs1.plot("First Plot", [random.random() for i in range(75)], 121)
        graphs1.plot("Second Plot", [random.random() for i in range(125)], 122)

        self.measurementGrid.addWidget(graphs1, 0, 0)

    def closeEvent(self, event):
        super().closeEvent(event)
        if self.video_window:
            self.video_window.close()
            
        self.video_window = None

    def refreshGamepad(self):
        # Sets the refresh boolean to true for the gamepad class to check for new gamepads in the new iteration.
        gp.GAMEPAD.needRefresh = True
        self.populateGamepads()

    def populateGamepads(self):
        self.menuGamepads.clear()
        gamepads = gp.GAMEPAD.get_all_gamepads()
        for id, name in gamepads.items():
            self.menuGamepads.addAction(str(id) + ": " + str(name))

    def initializeGamepad(self, gamepad):
        id, _ = gamepad.text().split(": ")
        gp.GAMEPAD.initialize(int(id))

    def setSpeedometerValue(self, value):
        self.speedMeter.display(value)

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

    @pyqtSlot('PyQt_PyObject')
    def receivedDataFromRover(self, data):
        # TODO Add more stuff here...
        if 'speed' in data:
            self.setSpeedometerValue(data['speed'])
            self.log.logData("Now running at {} m/s.".format(data['speed']), 0)

def loadMainWindow():
    wndw = MainWindow()
    wndw.showMaximized()
    wndw.openCameraWindow()
    return wndw