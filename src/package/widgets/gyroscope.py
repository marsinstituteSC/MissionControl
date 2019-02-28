from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
import sys

class GyroscopeWidget(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("designer/widget_gyro.ui", self)

    def setValues(self, X, Y, Z):
        self.lcd_roll.display(X)
        self.lcd_pitch.display(Y)
        self.lcd_yaw.display(Z)

    def setRoll(self, X):
        self.lcd_roll.display(X)

    def setPitch(self, Y):
        self.lcd_pitch.display(Y)

    def setYaw(self, Z):
        self.lcd_yaw.display(Z)