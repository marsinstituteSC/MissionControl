""" Display events stored in the DB """

from PyQt5.QtWidgets import QMainWindow, QHeaderView, QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt

from communications import database

EVENTLOG = None


class EventLogWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("designer/window_eventlog.ui", self)

        self.tabCategories.widget(
            0).findChild(QPushButton, "deleteSensorBtn").clicked.connect(self.delSelRowFromSensor)

        self.tableTabSensor = self.tabCategories.widget(
            0).findChild(QTableWidget, "sensorTable")

        header = self.tableTabSensor.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        data = database.Event.findByType(0)
        for row in data:
            idx = self.tableTabSensor.rowCount()
            self.tableTabSensor.insertRow(idx)
            msg = QTableWidgetItem(row.message)
            # Store the actual primary key here!
            msg.setData(Qt.UserRole, row.id)
            self.tableTabSensor.setItem(idx, 0, msg)
            self.tableTabSensor.setItem(idx, 1, QTableWidgetItem(row.type))
            self.tableTabSensor.setItem(idx, 2, QTableWidgetItem(row.severity))
            self.tableTabSensor.setItem(
                idx, 3, QTableWidgetItem(str(row.time)))

    def delSelRowFromSensor(self):
        row = self.tableTabSensor.currentRow()
        if row < 0:
            return

        id = self.tableTabSensor.item(row, 0).data(Qt.UserRole)
        self.tableTabSensor.removeRow(row)
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
