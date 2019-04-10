from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
import sys, random, time, json
from communications import udp_conn as UDP

class MotionControlWidget(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("designer/widget_motionControl.ui", self)
        self.mode = 0
        self.speed = 0.0
        self.turn = 0.0
        self.lineedit_speed.setText(str(0.0))
        self.lineedit_turn.setText(str(0.0))

        self.button_update.clicked.connect(self.updateMotion)
        self.combo_manipulation.currentIndexChanged.connect(self.disableInputs)
    
    def disableInputs(self, nr):
        self.lineedit_speed.setEnabled(not (nr != 0))
        self.lineedit_turn.setEnabled(not (nr != 0))

    def setMode(self, mode):
        self.mode = int(mode)
        self.disableInputs(int(mode))

    def getManualSpeed(self):
        try:
            return float(self.lineedit_speed.text())
        except:
            return 0.0

    def getManualTurn(self):
        try:
            return float(self.lineedit_turn.text())
        except:
            return 0.0

    def updateMotion(self):
        modeText = self.combo_manipulation.currentText()
        if modeText == "Manual":
            self.mode = 0
        elif modeText == "Relative Inverse Kinematic":
            self.mode = 1
        elif modeText == "Absolute Reverse Kinematic":
            self.mode = 2
        
        if self.mode == 0:
            self.speed = self.getManualSpeed()
            self.lineedit_speed.setText(str(self.speed))

            self.turn = self.getManualTurn()
            self.lineedit_turn.setText(str(self.turn))

        control = {"speed" : self.speed if self.mode == 0 else 0, "turn" : self.turn if self.mode == 0 else 0}
        manip = {"mode" : self.mode}
        message = {"manip" : manip, "control" : control}
        UDP.ROVERSERVER.writeToRover(json.dumps(message, separators=(',', ':')))    