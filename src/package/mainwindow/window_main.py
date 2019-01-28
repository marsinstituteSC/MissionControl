""" Main App Window, renders information from sensors, render graphs, etc... """

import PyQt5.QtWidgets
import PyQt5.uic
import random

from controls import plot
from controls import logger
from communications import udp_conn
from camera import window_video as wv
from settings import settings as cfg

class MainWindow(PyQt5.QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        PyQt5.uic.loadUi("designer/window_main.ui", self)
        self.setWindowTitle("JARL Viking III")    
        self.setupUi()

        # Creates the video window as a child and links a button to open it later
        self.video_window = None
        self.openCameraWindow()
        self.actionCamera_Window.triggered.connect(self.openCameraWindow)

        # Toolbar button to open settings
        self.actionSettings.triggered.connect(self.settings)

    def setupUi(self):
        """
        Load/Create UI controls, the toolbar has been created via the UI file.
        """
        mainWidget = PyQt5.QtWidgets.QWidget(self)
        mainGrid = PyQt5.QtWidgets.QGridLayout()
        self.setCentralWidget(mainWidget)            
        
        # TAB Box which contains multiple graphs for different type of sensors?
        sensorTABBox = PyQt5.QtWidgets.QTabWidget()
        
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
        miscWidget = PyQt5.QtWidgets.QWidget()        
        miscHBOX = PyQt5.QtWidgets.QHBoxLayout()
        miscWidget.setLayout(miscHBOX)
        
        self.speedMeter = PyQt5.QtWidgets.QLCDNumber()      
        self.speedMeter.setSegmentStyle(PyQt5.QtWidgets.QLCDNumber.Flat) 

        miscHBOX.addStretch()    
        miscHBOX.addWidget(PyQt5.QtWidgets.QLabel("Speed"))
        miscHBOX.addWidget(self.speedMeter)
        miscHBOX.addWidget(PyQt5.QtWidgets.QLabel("m/s"))
        self.setSpeedometerValue(12)    

        # Bottom section displays the log.
        log = logger.ColorizedLogger()
        log.logData("Anything, especially stuff we normally don't care about", 0)
        log.logData("Something normal happened", 1)
        log.logData("Something might be wrong", 2) 
        log.logData("Something is definitely wrong", 3)        
        
        mainGrid.addWidget(sensorTABBox, 1, 0)
        mainGrid.addWidget(miscWidget, 2, 0)
        mainGrid.addWidget(log, 3, 0)
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
            self.video_window.setWindowState(PyQt5.QtCore.Qt.WindowActive)

        self.video_window.activateWindow()


def loadMainWindow():
    wndw = MainWindow()
    wndw.showMaximized()
    wndw.openCameraWindow()
    return wndw
