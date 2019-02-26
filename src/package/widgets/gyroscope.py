from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, pyqtSlot, QObject
from PyQt5.QtWidgets import QApplication, QDialog, QWidget
from PyQt5.QtGui import QImage, QPixmap, QPainter
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = GyroscopeWidget()
    ex.show()
    ex.setValues(10,5,20)
    app.exec_()