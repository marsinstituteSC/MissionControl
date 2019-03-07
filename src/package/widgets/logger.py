""" 
    A simple logger which logs messages + priority, each priority is rendered using 
    a specific color.    
 """

from PyQt5.QtWidgets import QMainWindow, QMenu, QAction, QWidget, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi

from utils.math import clamp

import PyQt5.QtGui
import datetime
import cProfile

def getPriorityText(priority):
    if priority <= 0:
        return "Common"
    elif priority == 1:
        return "Notification"
    elif priority == 2:
        return "Warning"
    else:
        return "Error"

def getNameForRoverDataType(typ):
    if typ == 0:
        return "Speed"
    elif typ == 1:
        return "Temperature"

    return "Message"

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
        if p != 0: # Common priority uses default label color.
            item.setForeground(self.color)
        item.setData(Qt.UserRole, p)
        return item

class ColorizedLogger(QWidget):

    def __init__(self, parent=None, colorNotification=QColor(0, 255, 0), colorWarning=QColor(253, 106, 2), colorError=QColor(255, 0, 0)):
        super().__init__()
        self.setParent(parent)
        self.colorForPriority = [None, colorNotification, colorWarning, colorError]
        self.data = list()
        self.setupUi()

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
        self.checkPrioCommon.stateChanged.connect(self.display)
        self.checkPrioNotif.stateChanged.connect(self.display)
        self.checkPrioWarn.stateChanged.connect(self.display)
        self.checkPrioErr.stateChanged.connect(self.display)

        self.checkPrio = {
            0: self.checkPrioCommon,
            1: self.checkPrioNotif,
            2: self.checkPrioWarn,
            3: self.checkPrioErr
        }

        self.show()

    def getColorForPriority(self, priority):
        return self.colorForPriority[priority]

    def matchesCriteria(self, item, keyword):
        if len(keyword) <= 0:
            return True

        return (True if keyword.lower() in item.text.lower() else False)

    def logData(self, text, priority, type=0):
        """Log the data in a dictionary"""
        priority = clamp(priority, 0, (len(self.colorForPriority)-1))
        color = self.getColorForPriority(priority)
        tim = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item = LogItem(text, priority, tim, color, type)
        self.data.append(item)     

        # Check if we should add this data to the table right away:
        if (not self.checkFilterGUI.isChecked() and type is 0) or (not self.checkFilterRover.isChecked() and type is 1) or (not self.checkPrio[priority].isChecked()) or (not self.matchesCriteria(item, self.searchText.text())):
            return

        self.addNewRow(item)  
        self.loggerTable.scrollToBottom()

    def addNewRow(self, item):
        """Add a new item to the table itself"""
        index = self.loggerTable.rowCount()
        self.loggerTable.setRowCount(index + 1)      
        self.loggerTable.setItem(index, 0, item.getTableItem(item.text, item.priority))
        self.loggerTable.setItem(index, 1, item.getTableItem(getPriorityText(item.priority), item.priority))
        self.loggerTable.setItem(index, 2, item.getTableItem(item.timestamp, item.priority))          

    def display(self):
        search = self.searchText.text()
        self.loggerTable.clearContents()
        self.loggerTable.setRowCount(0)

        for v in self.data:
            if (not self.checkFilterGUI.isChecked() and v.type is 0) or (not self.checkFilterRover.isChecked() and v.type is 1) or (not self.checkPrio[v.priority].isChecked()) or (not self.matchesCriteria(v, search)):
                continue
                
            self.addNewRow(v)

        self.loggerTable.scrollToBottom()