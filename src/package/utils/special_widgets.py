""" Created classes of inherited classes for Qt for special uses """

from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, pyqtSlot, QObject
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QLabel
from PyQt5.QtGui import QImage, QPixmap, QPainter, QIcon
from PyQt5.uic import loadUi


class ClickableLabel(QLabel):
    clicked = pyqtSignal(str)

    def __init__(self, name):
        super().__init__()
        self.setObjectName(name)
        self.setScaledContents(True)

    def mousePressEvent(self, event):        
        self.clicked.emit(self.objectName())
        super().mousePressEvent(event)
