""" 
    A simple logger which logs messages + priority, each priority is rendered using 
    a specific color.    
 """

from PyQt5.QtWidgets import QMainWindow, QMenu, QAction, QWidget, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

from utils.math import clamp
from settings.settings import SETTINGSEVENT, SETTINGS

import PyQt5.QtGui
import datetime

# Log Item could be extended with SQL Alchemy to directly store the logged message to our sql database.
class LogItem():

    def __init__(self, text, priority, timestamp, color):
        super().__init__()
        self.text = text
        self.priority = priority
        self.timestamp = timestamp
        self.color = color

    def getTableItem(self, v, p):
        item = QTableWidgetItem(v)
        item.setForeground(self.color)
        item.setData(Qt.UserRole, p)
        return item


class ColorizedLogger(QTableWidget):

    def __init__(self, parent = None, colorCommon=QColor(0, 0, 0), colorNotification=QColor(0, 255, 0), colorWarning=QColor(253, 106, 2), colorError=QColor(255, 0, 0)):
        super().__init__()
        SETTINGSEVENT.addListener(self, self.onSettingsChanged)
        self.setParent(parent)
        self.colorForPriority = [colorCommon if (SETTINGS.get("main", "stylesheet") == "False") else QColor(255, 255, 255) , colorNotification, colorWarning, colorError]
        self.data = {
            "0": [],
            "1": [],
            "2": [],
            "3": []
        }
        self.setupUi()

    def __del__(self):
        if SETTINGSEVENT:
            SETTINGSEVENT.removeListener(self)

    def onSettingsChanged(self, name, params):
        self.colorForPriority[0] = QColor(0, 0, 0) if (params.get("main", "stylesheet") == "False") else QColor(255, 255, 255)
        for r in range(0, self.rowCount()): # Update the low prio. elements!
            priority = self.item(r, 0).data(Qt.UserRole)
            if priority == 0:
                self.item(r, 0).setForeground(self.colorForPriority[0])
                self.item(r, 1).setForeground(self.colorForPriority[0])
                self.item(r, 2).setForeground(self.colorForPriority[0])


    def setupUi(self):
        self.setEditTriggers(PyQt5.QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setColumnCount(3)
        self.setRowCount(0)
        self.verticalHeader().setVisible(False)
        self.setHorizontalHeaderLabels(["Message", "Priority", "Timestamp"])
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)        
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.show()

    def getColorForPriority(self, priority):
        return self.colorForPriority[priority]

    def getPriorityText(self, priority):
        if priority <= 0:
            return "Common"
        elif priority == 1:
            return "Notification"
        elif priority == 2:
            return "Warning"
        else:
            return "Error"

    def logData(self, text, priority):
        index = self.rowCount()
        self.setRowCount(index + 1)

        priority = clamp(priority, 0, (len(self.colorForPriority)-1))
        color = self.getColorForPriority(priority)
        tim = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item = LogItem(text, priority, tim, color)

        self.data.get(str(priority)).append(item) # TODO write to MySQL as well?
        # Set the desired item in the desired row , column
        self.setItem(index, 0, item.getTableItem(text, priority))
        self.setItem(index, 1, item.getTableItem(self.getPriorityText(priority), priority))
        self.setItem(index, 2, item.getTableItem(tim, priority))

        self.scrollToBottom()
