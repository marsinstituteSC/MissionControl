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
        self.btnMessage.clicked.connect(self.sendMessageNow)

        graph = plot.PlotCanvas(self, 10)
        # Make 1 row, 2 columns, 2 plots
        graph.plot("First Plot", [random.random() for i in range(25)], 121)
        graph.plot("Second Plot", [random.random() for i in range(25)], 122)
        graph.move(20, 20)

        log = logger.ColorizedLogger(self)
        log.setGeometry(0, 300, 400, 150)
        log.logData("Anything, especially stuff we normally don't care about", 0)
        log.logData("Something normal happened", 1)
        log.logData("Something might be wrong", 2) 
        log.logData("Something is definitely wrong", 3)

        # Creates the video window as a child and links a button to open it later
        self.video_window = None
        self.openCameraWindow()
        self.actionCamera_Window.triggered.connect(self.openCameraWindow)

        # Toolbar button to open settings
        self.actionSettings.triggered.connect(self.settings)

    def setSpeedometerValue(self, value):
        self.speedMeter.display(value)

    def sendMessageNow(self):  # Test test
        udp_conn.ROVERSERVER.writeToRover("Sending from App!")

    def settings(self):
        self.setting = cfg.openSettings()
    
    def openCameraWindow(self):
        self.video_window = wv.loadCameraWindow()


def loadMainWindow():
    wndw = MainWindow()
    wndw.show()
    return wndw
