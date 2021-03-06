""" Display events stored in the DB """

from PyQt5.QtWidgets import QMainWindow, QHeaderView, QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt

from communications import database
from widgets.logger import getNameForRoverDataType, getPriorityText
from widgets import logger as log

EVENTLOG = None

class EventLogWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("designer/window_eventlog.ui", self)

        self.deleteSensorBtn.clicked.connect(self.delSelRowFromSensor)

        header = self.sensorTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        data = database.Event.findAll(True)
        if data:
            if len(data) <= 0:
                log.LOGGER_EVENTS.dispatchDirectLogEvent("No entries found in the DB!", log.LOGGER_PRIORITY_NOTIFICATION)
            for row in data:
                idx = self.sensorTable.rowCount()
                self.sensorTable.insertRow(idx)
                msg = QTableWidgetItem(row.message)
                # Store the actual primary key here!
                msg.setData(Qt.UserRole, row.id)
                self.sensorTable.setItem(idx, 0, msg)
                self.sensorTable.setItem(idx, 1, QTableWidgetItem(getNameForRoverDataType(row.type)))
                self.sensorTable.setItem(idx, 2, QTableWidgetItem(getPriorityText(row.severity)))
                self.sensorTable.setItem(
                    idx, 3, QTableWidgetItem(str(row.time)))
        else:
            log.LOGGER_EVENTS.dispatchDirectLogEvent("Unable to connect and read from the DB!", log.LOGGER_PRIORITY_ERROR)

    def delSelRowFromSensor(self):
        row = self.sensorTable.currentRow()
        if row < 0:
            return

        id = self.sensorTable.item(row, 0).data(Qt.UserRole)
        self.sensorTable.removeRow(row)
        database.Event.delete(id)

    def closeEvent(self, event):
        super().closeEvent(event)
        global EVENTLOG
        EVENTLOG = None


def showEventLog():
    global EVENTLOG
    if EVENTLOG is None:
        EVENTLOG = EventLogWindow()

    EVENTLOG.show()
    EVENTLOG.activateWindow()
    return EVENTLOG

def closeEventLog():
    global EVENTLOG
    if EVENTLOG:
        EVENTLOG.close()
        EVENTLOG = None