from PyQt5.QtWidgets import QWidget
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
        self.lineedit_speed.setText(str(0.0))
        self.lineedit_turn.setText(str(0.0))

        self.button_update.clicked.connect(self.updateMotion)
        self.combo_manipulation.currentIndexChanged.connect(self.disableInputs)
    
    def disableInputs(self, nr):
        if nr != 0:
            self.lineedit_speed.setEnabled(False)
            self.lineedit_turn.setEnabled(False)
        else:
            self.lineedit_speed.setEnabled(True)
            self.lineedit_turn.setEnabled(True)

    def setMode(self, mode):
        self.mode = int(mode)
        self.disableInputs(int(mode))

    def updateMotion(self):
        modeText = self.combo_manipulation.currentText()
        if modeText == "Manual":
            self.mode = 0
        elif modeText == "Relative Inverse Kinematic":
            self.mode = 1
        elif modeText == "Absolute Reverse Kinematic":
            self.mode = 2
        
        if self.mode == 0:
            try:
                self.speed = (float(self.lineedit_speed.text()))
            except:
                self.speed = 0.0
                self.lineedit_speed.setText(str(0.0))
            
            try:
                self.turn = (float(self.lineedit_turn.text()))
            except:
                self.turn = 0.0
                self.lineedit_turn.setText(str(0.0))

        control = {"speed" : self.speed if self.mode == 0 else 0, "turn" : self.turn if self.mode == 0 else 0}
        manip = {"mode" : self.mode}
        output = {"manip" : manip, "control" : control}
        #ROVERSERVER.writeToRover(output)