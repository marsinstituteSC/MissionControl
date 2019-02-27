from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, pyqtSlot, QObject, QPoint
from PyQt5.QtWidgets import QApplication, QDialog, QWidget
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPalette, QFont, QFontMetricsF, QPen, QPolygon, QColor
from PyQt5.uic import loadUi
import sys, random, time

class Compass(QWidget):
    def __init__(self):
        super().__init__()

        self.setMaximumHeight(300)
        self.setMaximumWidth(300)
        self.setMinimumHeight(100)
        self.setMinimumWidth(100)
        self.angle = 0
        self.margins = 10
        self.directions = {
            0 : "N",
            45 : "NE",
            90 : "E",
            135 : "SE",
            180 : "S",
            225 : "SW",
            270 : "W",
            315 : "NW"
        }
        self.activated = False

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if not self.activated:
            self.drawDirections(painter)
        self.drawNeedle(painter)
        painter.end()

    def drawDirections(self, painter):
        painter.save()
        painter.translate(self.width()/2, self.height()/2) # Centers the position on the widget.
        scale = min((self.width() - self.margins) / 120, (self.height() - self.margins) / 120)
        painter.scale(scale, scale)

        font = QFont(self.font())
        font.setPixelSize(10)
        metrics = QFontMetricsF(font)

        painter.setFont(font)
        painter.setPen(self.palette().color(QPalette.Shadow))

        i = 0
        while i < 360:
            # Check if it should draw the directions or if it should draw the lines between the directions.
            if i % 45 == 0:
                painter.drawLine(0, -40, 0, -50)
                painter.drawText(-metrics.width(self.directions[i]) / 2, -52, self.directions[i])
            else:
                painter.drawLine(0, -45, 0, -50)
            painter.rotate(15)
            i += 15
        painter.restore()

    def drawNeedle(self, painter):
        painter.save()
        painter.translate(self.width()/2, self.height()/2)
        painter.rotate(self.angle)
        scale = min((self.width() - self.margins) / 120, (self.height() - self.margins) / 120)
        painter.scale(scale, scale)

        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(QColor(Qt.black))
        painter.drawPolygon(QPolygon([QPoint(-10, 0), QPoint(0, -45), QPoint(10, 0), QPoint(0, 45), QPoint(-10, 0)]))

        painter.setBrush(QColor(Qt.red))
        painter.drawPolygon(QPolygon([QPoint(-5, -25), QPoint(0, -45), QPoint(5, -25), QPoint(0, -30), QPoint(-5, -25)]))
        painter.restore()

    def setAngle(self, angle):
        if angle != self.angle:
            self.angle = angle
            self.update()
    
    def getAngle(self):
        return self.angle

class CompassWidget(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("designer/widget_compass.ui", self)
        self.compass = Compass()
        self.gridLayout_3.addWidget(self.compass, 0, 0)
        self.label.setText(str(self.compass.getAngle()) + "º")

    def setAngleCompass(self, angle):
        self.compass.setAngle(angle)
        self.label.setText(str(angle) + "º")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CompassWidget()
    win.show()
    win.setAngleCompass(300)
    sys.exit(app.exec_())