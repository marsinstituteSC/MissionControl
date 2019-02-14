""" 
    A simple logger which logs messages + priority, each priority is rendered using 
    a specific color.    
 """

from PyQt5.QtWidgets import QMainWindow, QMenu, QAction, QWidget, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi

from utils.math import clamp
from settings.settings import SETTINGSEVENT, SETTINGS

import PyQt5.QtGui
import datetime
import cProfile

# Log Item could be extended with SQL Alchemy to directly store the logged message to our sql database.
class LogItem():

    def __init__(self, text, priority, timestamp, color, type):
        super().__init__()
        self.text = text
        self.priority = priority
        self.timestamp = timestamp
        self.color = color
        self.type = type

    def getTableItem(self, v, p):
        item = QTableWidgetItem(v)
        item.setForeground(self.color)
        item.setData(Qt.UserRole, p)
        return item

class ColorizedLogger(QWidget):

    def __init__(self, parent=None, colorCommon=QColor(0, 0, 0), colorNotification=QColor(0, 255, 0), colorWarning=QColor(253, 106, 2), colorError=QColor(255, 0, 0)):
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
        for r in range(0, self.loggerTable.rowCount()): # Update the low prio. elements!
            priority = self.loggerTable.item(r, 0).data(Qt.UserRole)
            if priority == 0:
                self.loggerTable.item(r, 0).setForeground(self.colorForPriority[0])
                self.loggerTable.item(r, 1).setForeground(self.colorForPriority[0])
                self.loggerTable.item(r, 2).setForeground(self.colorForPriority[0])

    def keyPressEvent(self, e):
        super().keyPressEvent(e)
        if e.key() == Qt.Key_Return or e.key() == Qt.Key_F5:
            self.display()

    def setupUi(self):
        loadUi("designer/widget_logger.ui", self)
        header = self.loggerTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)        
        self.searchButton.clicked.connect(self.display)
        self.checkFilterGUI.stateChanged.connect(self.display)
        self.checkFilterRover.stateChanged.connect(self.display)
        self.comboPriorities.currentIndexChanged.connect(self.display)
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

    def matchesCriteria(self, item, keyword):
        if len(keyword) <= 0:
            return True

        return (True if keyword.lower() in item.text.lower() else False)

    def logData(self, text, priority, type=0):
        """Log the data in a dictionary"""
        prioChoice = (self.comboPriorities.currentIndex() - 1)
        priority = clamp(priority, 0, (len(self.colorForPriority)-1))
        color = self.getColorForPriority(priority)
        tim = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item = LogItem(text, priority, tim, color, type)
        self.data.get(str(priority)).append(item)     

        # Check if we should add this data to the table right away:
        if (not self.checkFilterGUI.isChecked() and type is 0) or (not self.checkFilterRover.isChecked() and type is 1) or ((prioChoice >= 0) and prioChoice is not item.priority) or (not self.matchesCriteria(item, self.searchText.text())):
            return

        self.addNewRow(item)  

    def addNewRow(self, item):
        """Add a new item to the table itself"""
        index = self.loggerTable.rowCount()
        self.loggerTable.setRowCount(index + 1)      
        self.loggerTable.setItem(index, 0, item.getTableItem(item.text, item.priority))
        self.loggerTable.setItem(index, 1, item.getTableItem(self.getPriorityText(item.priority), item.priority))
        self.loggerTable.setItem(index, 2, item.getTableItem(item.timestamp, item.priority))  
        self.loggerTable.scrollToBottom()

    def display(self):
        search = self.searchText.text()
        prioChoice = (self.comboPriorities.currentIndex() - 1)
        self.loggerTable.clearContents()
        self.loggerTable.setRowCount(0)

        for p, _ in self.data.items():
            for v in self.data[p]:
                if (not self.checkFilterGUI.isChecked() and v.type is 0) or (not self.checkFilterRover.isChecked() and v.type is 1) or ((prioChoice >= 0) and prioChoice is not v.priority) or (not self.matchesCriteria(v, search)):
                    continue
                    
                self.addNewRow(v)