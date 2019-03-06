from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize
from PyQt5.uic import loadUi
import sys

class ControlStatus(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("designer/widget_controlStatus.ui", self)
        self.iconOn = QIcon("images/status icons/light_green_original.png")
        self.iconOff = QIcon("images/status icons/light_red_original.png")

        self.label_rover_status.setPixmap(self.iconOff.pixmap(QSize(64,64)))
        self.label_database_status.setPixmap(self.iconOff.pixmap(QSize(64,64)))
        self.label_controller_status.setPixmap(self.iconOff.pixmap(QSize(64,64)))

    def setRoverStatus(self, status):
        self.label_rover_status.setPixmap(self.iconOn.pixmap(QSize(64,64)) if status else self.iconOff.pixmap(QSize(64,64)))
    
    def setControllerStatus(self, status):
        self.label_controller_status.setPixmap(self.iconOn.pixmap(QSize(64,64)) if status else self.iconOff.pixmap(QSize(64,64)))
    
    def setDatabaseStatus(self, status):
        self.label_database_status.setPixmap(self.iconOn.pixmap(QSize(64,64)) if status else self.iconOff.pixmap(QSize(64,64)))