from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, pyqtSlot, QObject, QPoint
from PyQt5.QtWidgets import QApplication, QDialog, QWidget
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPalette, QFont, QFontMetricsF, QPen, QPolygon, QColor
from PyQt5.uic import loadUi
import sys, random, time
from communications.udp_conn import ROVERSERVER

class MotionControlWidget(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("designer/widget_motionControl.ui", self)
        self.mode = 0
        self.speed = 0.0
        self.turn = 0.0
        self.speedLineEdit.setText(str(0.0))
        self.turnLineEdit.setText(str(0.0))

        self.updateMotionButton.clicked.connect(self.updateMotion)
        self.manipMode.currentIndexChanged.connect(self.disableInputs)
    
    def disableInputs(self, nr):
        if nr != 0:
            self.speedLineEdit.setEnabled(False)
            self.turnLineEdit.setEnabled(False)
        else:
            self.speedLineEdit.setEnabled(True)
            self.turnLineEdit.setEnabled(True)

    def setMode(self, mode):
        self.mode = int(mode)
        self.disableInputs(int(mode))

    def updateMotion(self):
        modeText = self.manipMode.currentText()
        if modeText == "Manual":
            self.mode = 0
        elif modeText == "Relative Inverse Kinematic":
            self.mode = 1
        elif modeText == "Absolute Reverse Kinematic":
            self.mode = 2
        
        if self.mode == 0:
            try:
                self.speed = (float(self.speedLineEdit.text()))
            except:
                self.speed = 0.0
                self.speedLineEdit.setText(str(0.0))
            
            try:
                self.turn = (float(self.turnLineEdit.text()))
            except:
                self.turn = 0.0
                self.turnLineEdit.setText(str(0.0))

        control = {"speed" : self.speed if self.mode == 0 else 0, "turn" : self.turn if self.mode == 0 else 0}
        manip = {"mode" : self.mode}
        output = {"manip" : manip, "control" : control}
        #ROVERSERVER.writeToRover(output)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MotionControlWidget()
    win.show()
    sys.exit(app.exec_())