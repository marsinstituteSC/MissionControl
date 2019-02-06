""" Main App Window, renders information from sensors, render graphs, etc... """

import random

from PyQt5.QtWidgets import QMainWindow, QWidget, QTabWidget, QLCDNumber, QHBoxLayout, QLabel, QGridLayout
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

from controls import plot
from controls import logger
from communications import udp_conn
from camera import window_video as wv
from settings import settings as cfg
from mainwindow import window_eventlog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("designer/window_main.ui", self)
        self.setWindowTitle("JARL Viking III")    
        self.setupUi()

        # Creates the video window as a child and links a button to open it later
        self.video_window = None
        self.openCameraWindow()
        self.actionCamera_Window.triggered.connect(self.openCameraWindow)

        # Toolbar button to open settings
        self.actionSettings.triggered.connect(self.settings)
        self.actionLog.triggered.connect(window_eventlog.showEventLog)

        udp_conn.ROVERSERVER.onReceiveData.connect(self.receivedDataFromRover)

    def setupUi(self):
        """
        Load/Create UI controls, the toolbar has been created via the UI file.
        """
        mainWidget = QWidget(self)
        mainGrid = QGridLayout()
        self.setCentralWidget(mainWidget)            
        
        # TAB Box which contains multiple graphs for different type of sensors?
        sensorTABBox = QTabWidget()
        
        # Make 1 row, 2 columns, 2 plots
        graphs1 = plot.PlotCanvas(None, 10)
        graphs1.plot("First Plot", [random.random() for i in range(25)], 121)
        graphs1.plot("Second Plot", [random.random() for i in range(25)], 122)

        graphs2 = plot.PlotCanvas(None, 10)        
        graphs2.plot("First Plot", [random.random() for i in range(75)], 121)
        graphs2.plot("Second Plot", [random.random() for i in range(125)], 122)        

        sensorTABBox.addTab(graphs1, "Temperature")
        sensorTABBox.addTab(graphs2, "Velocity")

        # Misc section could contain speed, accel, sensor readings, etc...
        miscWidget = QWidget()        
        miscHBOX = QHBoxLayout()
        miscWidget.setLayout(miscHBOX)
        
        self.speedMeter = QLCDNumber()      
        self.speedMeter.setSegmentStyle(QLCDNumber.Flat) 

        miscHBOX.addStretch()    
        miscHBOX.addWidget(QLabel("Speed"))
        miscHBOX.addWidget(self.speedMeter)
        miscHBOX.addWidget(QLabel("m/s"))
        self.setSpeedometerValue(12)    

        # Bottom section displays the log.
        self.log = logger.ColorizedLogger()
        self.log.logData("Anything, especially stuff we normally don't care about", 0)
        self.log.logData("Something normal happened", 1)
        self.log.logData("Something might be wrong", 2) 
        self.log.logData("Something is definitely wrong", 3)        
        
        mainGrid.addWidget(sensorTABBox, 1, 0)
        mainGrid.addWidget(miscWidget, 2, 0)
        mainGrid.addWidget(self.log, 3, 0)
        mainGrid.setRowStretch(1, 50)
        mainGrid.setRowStretch(3, 20)
        mainWidget.setLayout(mainGrid)

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
