from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
import sys

class GyroscopeWidget(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("designer/widget_gyro.ui", self)

    def setValues(self, X, Y, Z):
        self.rotationX.display(X)
        self.rotationY.display(Y)
        self.rotationZ.display(Z)