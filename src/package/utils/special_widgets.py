""" Created classes of inherited classes for Qt for special uses """

from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, pyqtSlot, QObject
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QLabel, QGroupBox, QPushButton, QGridLayout
from PyQt5.QtGui import QImage, QPixmap, QPainter, QIcon, QCursor, QFont
from PyQt5.uic import loadUi


class ClickableLabel(QLabel):
    clicked = pyqtSignal(str)

    def __init__(self, name, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(name)
        self.setScaledContents(True)
        self.setAlignment(Qt.AlignCenter)

    def mousePressEvent(self, event):        
        self.clicked.emit(self.objectName())
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        self.setCursor(QCursor(Qt.PointingHandCursor))

class ClickableGroupBox(QWidget):
    clicked = pyqtSignal()

    def __init__(self, title):
        super().__init__()
        self.layout = QGridLayout(self)
        self.titleButton = ClickableLabel("Functions", parent=self)
        self.titleButton.setText("Functions")
        self.titleButton.move(0,-10)
        font = QFont()
        font.setBold(True)
        self.titleButton.setFont(font)