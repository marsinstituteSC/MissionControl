""" 
    A simple logger which logs messages + priority, each priority is rendered using 
    a specific color.    
 """

from PyQt5.QtWidgets import QMainWindow, QMenu, QAction, QWidget, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QObject
from PyQt5.uic import loadUi

from utils.math import clamp

import PyQt5.QtGui
import datetime
import cProfile

# Constants, used instead of magic numbers.

LOGGER_PRIORITY_COMMON = 0
LOGGER_PRIORITY_NOTIFICATION = 1
LOGGER_PRIORITY_WARNING = 2
LOGGER_PRIORITY_ERROR = 3

LOGGER_TYPE_GUI = 0
LOGGER_TYPE_ROVER = 1

LOGGER_DATA_TYPE_SPEED = 0
LOGGER_DATA_TYPE_TEMPERATURE = 1

def getPriorityText(priority):
    if priority <= LOGGER_PRIORITY_COMMON:
        return "Common"
    elif priority == LOGGER_PRIORITY_NOTIFICATION:
        return "Notification"
    elif priority == LOGGER_PRIORITY_WARNING:
        return "Warning"
    else:
        return "Error"

def getNameForRoverDataType(typ):
    if typ == LOGGER_DATA_TYPE_SPEED:
        return "Speed"
    elif typ == LOGGER_DATA_TYPE_TEMPERATURE:
        return "Temperature"

    return "Message"

class LoggerEvents(QObject):
    """
    Dispatches cross-thread log events, directly to the logger.
    Can also be used to log directly on the same thread using dispatchDirectLogEvent.
    """
    logMessage = pyqtSignal(str, int, int)

    def __init__(self):
        super().__init__()
        self.logger = None

    def __del__(self):
        self.logger = None

    def dispatchLogEvent(self, msg, priority, typ=0):
        self.logMessage.emit(str(msg), int(priority), int(typ))

    def dispatchDirectLogEvent(self, msg, priority, typ=0):
        if self.logger:
            self.logger.logData(str(msg), int(priority), int(typ))

    def bind(self, obj):
        """
        Bind this global to the actual logger object.
        """
        self.logger = obj

LOGGER_EVENTS = LoggerEvents()

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
        self.filterToggle = True
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

        LOGGER_EVENTS.logMessage.connect(self.logData)
        LOGGER_EVENTS.bind(self)

        self.searchButton.clicked.connect(self.display)
        self.checkFilterGUI.stateChanged.connect(self.display)
        self.checkFilterRover.stateChanged.connect(self.display)
        self.checkPrioCommon.stateChanged.connect(self.display)
        self.checkPrioNotif.stateChanged.connect(self.display)
        self.checkPrioWarn.stateChanged.connect(self.display)
        self.checkPrioErr.stateChanged.connect(self.display)

        self.filterButton.clicked.connect(self.toggleFilter)
        self.toggleFilter()

        self.checkPrio = {
            LOGGER_PRIORITY_COMMON: self.checkPrioCommon,
            LOGGER_PRIORITY_NOTIFICATION: self.checkPrioNotif,
            LOGGER_PRIORITY_WARNING: self.checkPrioWarn,
            LOGGER_PRIORITY_ERROR: self.checkPrioErr
        }

        self.show()

    def toggleFilter(self):
        if self.filterToggle:
            self.filterToggle = False
            self.filterBox.hide()
            self.filterButton.setText("Show Filters")
        else:
            self.filterToggle = True
            self.filterBox.show()
            self.filterButton.setText("Hide Filters")

    def getColorForPriority(self, priority):
        return self.colorForPriority[priority]

    def matchesCriteria(self, item, keyword):
        if len(keyword) <= 0:
            return True

        return (True if keyword.lower() in item.text.lower() else False)

    @pyqtSlot(str, int, int)
    def logData(self, text, priority, type=0):
        """Log the data in a dictionary"""
        priority = clamp(priority, 0, (len(self.colorForPriority)-1))
        color = self.getColorForPriority(priority)
        tim = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item = LogItem(text, priority, tim, color, type)
        self.data.append(item)     

        # Check if we should add this data to the table right away:
        if (not self.checkFilterGUI.isChecked() and type is LOGGER_TYPE_GUI) or (not self.checkFilterRover.isChecked() and type is LOGGER_TYPE_ROVER) or (not self.checkPrio[priority].isChecked()) or (not self.matchesCriteria(item, self.searchText.text())):
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
            if (not self.checkFilterGUI.isChecked() and v.type is LOGGER_TYPE_GUI) or (not self.checkFilterRover.isChecked() and v.type is LOGGER_TYPE_ROVER) or (not self.checkPrio[v.priority].isChecked()) or (not self.matchesCriteria(v, search)):
                continue
                
            self.addNewRow(v)

        self.loggerTable.scrollToBottom()
