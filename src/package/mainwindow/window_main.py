""" Main App Window, renders information from sensors, render graphs, etc... """

import PyQt5.QtWidgets
import PyQt5.uic
import random

from plotting import plot
from communications import udp_conn


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

    def setSpeedometerValue(self, value):
        self.speedMeter.display(value)

    def sendMessageNow(self):  # Test test
        udp_conn.ROVERSERVER.writeToRover("Sending from App!")


def loadMainWindow():
    wndw = MainWindow()
    wndw.show()
    return wndw
