from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize
from PyQt5.uic import loadUi
import sys

class SpeedWidget(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("designer/widget_speed.ui", self)
        self.speed = 0
        self.turn = 0

        self.speedIcons = {
            "stop" : QIcon("images/status icons/speed_stop.png"),
            "fwd_slow" : QIcon("images/status icons/speed_fwd_slow.png"),
            "fwd_med" : QIcon("images/status icons/speed_fwd_medium.png"),
            "fwd_fast" : QIcon("images/status icons/speed_fwd_fast.png"),
            "bck_slow" : QIcon("images/status icons/speed_bck_slow.png"),
            "bck_med" : QIcon("images/status icons/speed_bck_medium.png"),
            "bck_fast" : QIcon("images/status icons/speed_bck_fast.png")
        }
        self.turnIcons = {
            "fwd" : QIcon("images/status icons/turn_straight.png"),
            "left" : QIcon("images/status icons/turn_left.png"),
            "right" : QIcon("images/status icons/turn_right.png")
        }
        self.setSpeed(0)
        self.setTurn(-5)
    
    def setSpeed(self, speed):
        self.speed = int(speed)
        self.lcd_speed.display(self.speed)
        # Dont know what fast is in the context of the rover, using 1 as slow, 2 as medium and 3 as fast.
        if self.speed == 0:
            self.label_speed_image.setPixmap(self.speedIcons["stop"].pixmap(QSize(64,64)))
        elif self.speed > 0 and self.speed <= 1:
            self.label_speed_image.setPixmap(self.speedIcons["fwd_slow"].pixmap(QSize(64,64)))
        elif self.speed > 1 and self.speed <= 2:
            self.label_speed_image.setPixmap(self.speedIcons["fwd_med"].pixmap(QSize(64,64)))
        elif self.speed > 2:
            self.label_speed_image.setPixmap(self.speedIcons["fwd_fast"].pixmap(QSize(64,64)))
        elif self.speed < 0 and self.speed >= -1:
            self.label_speed_image.setPixmap(self.speedIcons["bck_slow"].pixmap(QSize(64,64)))
        elif self.speed < -1 and self.speed >= -2:
            self.label_speed_image.setPixmap(self.speedIcons["bck_med"].pixmap(QSize(64,64)))
        elif self.speed < -2:
            self.label_speed_image.setPixmap(self.speedIcons["bck_fast"].pixmap(QSize(64,64)))
    
    def setTurn(self, turn):
        self.turn = int(turn)
        if self.turn == 0:
            self.label_turn_image.setPixmap(self.turnIcons["fwd"].pixmap(QSize(64,64)))
        elif self.turn > 0:
            self.label_turn_image.setPixmap(self.turnIcons["left"].pixmap(QSize(64,64)))
        elif self.turn < 0:
            self.label_turn_image.setPixmap(self.turnIcons["right"].pixmap(QSize(64,64)))