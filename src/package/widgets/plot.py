""" Mathplot for plotting graphs - https://pythonspot.com/pyqt5-matplotlib/ """

from PyQt5.QtWidgets import QMainWindow, QMenu, QAction, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton, QFileDialog

import PyQt5.QtGui
import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from settings.settings import SETTINGSEVENT, SETTINGS

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.patch.set_facecolor("None")  # Make background transparent.        
        super().__init__(fig)
        SETTINGSEVENT.addListener(self, self.onSettingsChanged)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(
            self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.setStyleSheet(
            self, "background-color:transparent;")  # No BG!
        FigureCanvas.updateGeometry(self)        

    def __del__(self):
        if SETTINGSEVENT:
            SETTINGSEVENT.removeListener(self)

    def onSettingsChanged(self, name, params):
        self.loadSettings(params)

    def loadSettings(self, config):
        """
        Settings updated/loaded, set the correct colors!
        """
        color = 'black' if (config.get("main", "stylesheet") == "False") else 'white'
        for ax in self.figure.axes:
            ax.tick_params(axis='x', colors=color)
            ax.tick_params(axis='y', colors=color)
            ax.yaxis.label.set_color(color)
            ax.xaxis.label.set_color(color)
            ax.title.set_color(color)
        self.draw()


    def plot(self, title, data, subplot):
        """Plot the graph given the title, data and subplot"""
        self.figure.clear()
        ax = self.figure.add_subplot(subplot)
        ax.plot(data, 'r-')
        ax.set_title(title)
        ax.patch.set_facecolor("white")
        ax.patch.set_alpha(0.5)
        self.loadSettings(SETTINGS)

    def save(self):
        """Save plot as a transparent png file."""
        # Have to use self.window() rather than just self, due to QFileDialog will inherit stylesheet, making the dialog transparent and buggy...
        fileName, _ = QFileDialog.getSaveFileName(self.window(),"Save plot(s)","","All Files (*);;PNG Files (*.png)", options=(QFileDialog.Options() | QFileDialog.DontUseNativeDialog))
        if fileName:
            self.figure.savefig(fileName, facecolor=self.figure.get_facecolor(), edgecolor='none', transparent=True)        

    def contextMenuEvent(self, event):
        """Handle right-click context menu event"""
        super().contextMenuEvent(event)

        menu = QMenu(self.window())

        actionSave = QAction("Save", self)
        actionSave.triggered.connect(lambda: self.save())

        menu.addAction(actionSave)
        menu.popup(PyQt5.QtGui.QCursor.pos())
