from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi
import sys

from utils.warning import showWarning
from utils.special_widgets import ClickableLabel

class SimpleStatus(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("designer/widget_simpleStatus.ui", self)
        # List of wheel names for easy search later
        self.wheelNames = ["frontLeftWheel", "frontRightWheel", "middleLeftWheel", "middleRightWheel", "backLeftWheel", "backRightWheel"]
        self.statusIcons = {
            "wheelok" : QPixmap("images/status icons/small_wheel_ok.png"),
            "wheelfault" : QPixmap("images/status icons/small_wheel_fault.png"),
            "cameraok" : QPixmap("images/status icons/camera_ok.png"),
            "camerafault" : QPixmap("images/status icons/camera_fault.png"),
            "manipulatorok" : QPixmap("images/status icons/manipulator_ok.png"),
            "manipulatorfault" : QPixmap("images/status icons/manipulator_fault.png"),
            "mainok" : QPixmap("images/status icons/main_ok.png"),
            "mainfault" : QPixmap("images/status icons/main_fault.png")
        }
        # Contains the messages
        self.status = {
            "frontLeftWheel" : None,
            "frontRightWheel" : None,
            "middleLeftWheel" : None,
            "middleRightWheel" : None,
            "backLeftWheel" : None,
            "backRightWheel" : None,
            "camera" : None,
            "manipulator" : None,
            "main" : None
        }

        self.createLabels()

        self.resetImages()

    def createLabels(self):
        """ Creates the special labels and assigns them onto the grid """
        self.frontLeftWheel = ClickableLabel("frontLeftWheel")
        self.frontLeftWheel.clicked.connect(self.showWarning)
        self.gridLayout.addWidget(self.frontLeftWheel, 0, 0)
        
        self.frontRightWheel = ClickableLabel("frontRightWheel")
        self.frontRightWheel.clicked.connect(self.showWarning)
        self.gridLayout.addWidget(self.frontRightWheel, 0, 2)

        self.middleLeftWheel = ClickableLabel("middleLeftWheel")
        self.middleLeftWheel.clicked.connect(self.showWarning)
        self.gridLayout.addWidget(self.middleLeftWheel, 1, 0)

        self.middleRightWheel = ClickableLabel("middleRightWheel")
        self.middleRightWheel.clicked.connect(self.showWarning)
        self.gridLayout.addWidget(self.middleRightWheel, 1, 2)

        self.backLeftWheel = ClickableLabel("backLeftWheel")
        self.backLeftWheel.clicked.connect(self.showWarning)
        self.gridLayout.addWidget(self.backLeftWheel, 2, 0)

        self.backRightWheel = ClickableLabel("backRightWheel")
        self.backRightWheel.clicked.connect(self.showWarning)
        self.gridLayout.addWidget(self.backRightWheel, 2, 2)

        grid = QGridLayout()

        self.manipulator = ClickableLabel("manipulator")
        self.manipulator.clicked.connect(self.showWarning)
        grid.addWidget(self.manipulator, 0, 0)

        self.camera = ClickableLabel("camera")
        self.camera.clicked.connect(self.showWarning)
        grid.addWidget(self.camera, 0, 1)

        self.gridLayout.addLayout(grid, 0, 1)

        self.main = ClickableLabel("main")
        self.main.clicked.connect(self.showWarning)
        self.gridLayout.addWidget(self.main, 1, 1, 2, 1)

    # NOTE: DO NOT STOP THE WINDOW UNDER THE ERROR FROM BEING CLICKED
    def showWarning(self, part):
        if self.status[part]:
            text = ""
            for txt in self.status[part]:
                text += txt + "\n"
            showWarning("Issues", text)

    def resetImages(self):
        """ Resets the images """
        self.frontLeftWheel.setPixmap(self.statusIcons["wheelok"])
        self.frontRightWheel.setPixmap(self.statusIcons["wheelok"])
        self.middleLeftWheel.setPixmap(self.statusIcons["wheelok"])
        self.middleRightWheel.setPixmap(self.statusIcons["wheelok"])
        self.backLeftWheel.setPixmap(self.statusIcons["wheelok"])
        self.backRightWheel.setPixmap(self.statusIcons["wheelok"])
        self.manipulator.setPixmap(self.statusIcons["manipulatorok"])
        self.camera.setPixmap(self.statusIcons["cameraok"])
        self.main.setPixmap(self.statusIcons["mainok"])

    def setWheelStatus(self, error, wheel):
        """ Changes the displayed image of the wheels, depending on the error status """
        if wheel == "frontLeftWheel":
            if error:
                self.frontLeftWheel.setPixmap(self.statusIcons["wheelfault"])
            else:
                self.frontLeftWheel.setPixmap(self.statusIcons["wheelok"])
        elif wheel == "frontRightWheel":
            if error:
                self.frontRightWheel.setPixmap(self.statusIcons["wheelfault"])
            else:
                self.frontRightWheel.setPixmap(self.statusIcons["wheelok"])
        elif wheel == "middleLeftWheel":
            if error:
                self.middleLeftWheel.setPixmap(self.statusIcons["wheelfault"])
            else:
                self.middleLeftWheel.setPixmap(self.statusIcons["wheelok"])
        elif wheel == "middleRightWheel":
            if error:
                self.middleRightWheel.setPixmap(self.statusIcons["wheelfault"])
            else:
                self.middleRightWheel.setPixmap(self.statusIcons["wheelok"])
        elif wheel == "backLeftWheel":
            if error:
                self.backLeftWheel.setPixmap(self.statusIcons["wheelfault"])
            else:
                self.backLeftWheel.setPixmap(self.statusIcons["wheelok"])
        elif wheel == "backRightWheel":
            if error:
                self.backRightWheel.setPixmap(self.statusIcons["wheelfault"])
            else:
                self.backRightWheel.setPixmap(self.statusIcons["wheelok"])

    def setCameraStatus(self, error):
        """ Sets the status image for the camera """
        if error:
            self.camera.setPixmap(self.statusIcons["camerafault"])
        else:
            self.camera.setPixmap(self.statusIcons["cameraok"])

    def setManipulatorStatus(self, error):
        """ Sets the status image for the manipulator """
        if error:
            self.manipulator.setPixmap(self.statusIcons["manipulatorfault"])
        else:
            self.manipulator.setPixmap(self.statusIcons["manipulatorok"])
        
    def setBodyStatus(self, error):
        """
        Sets the status image and text for the body
        Body will be affected by every error that has not a specific area in the grid, ex wheels.
        """
        if error:
            self.main.setPixmap(self.statusIcons["mainfault"])
        else:
            self.main.setPixmap(self.statusIcons["mainok"])

    def statusHandler(self, status):
        """
        Handler to set the correct image and messages from the incoming dictionary

        Expected status dictionary:
        key - see key names in exampleData's status dictionary
        status - Boolean to quckly tell if there is an error, false will reset the state.
        messages - list of error messages from the rover on that part.
        """
        if not status:
            return
        for part, message in status.items():
            if part in self.wheelNames:
                if bool(message["error"]):
                    self.setWheelStatus(True, part)
                    self.status[part] = message["messages"]
                else:
                    self.setWheelStatus(False, part)
                    self.status[part] = None
            elif part == "camera":
                if bool(message["error"]):
                    self.setCameraStatus(True)
                    self.status[part] = message["messages"]
                else:
                    self.setCameraStatus(False)
                    self.status[part] = None
            elif part == "manipulator":
                if bool(message["error"]):
                    self.setManipulatorStatus(True)
                    self.status[part] = message["messages"]
                else:
                    self.setManipulatorStatus(False)
                    self.status[part] = None
            elif part == "main":
                if bool(message["error"]):
                    self.setBodyStatus(True)
                    self.status[part] = message["messages"]
                else:
                    self.setBodyStatus(False)
                    self.status[part] = None

def exampleData():
    flw = {
        "error" : False,
        "messages" : None
    }
    frw = { # Front Right Wheel
        "error" : False,
        "messages" : None
    }
    mlw = { # Middle Left Wheel
        "error" : False,
        "messages" : None
    }
    mrw = { # Middle Right Wheel
        "error" : False,
        "messages" : None
    }
    blw = { # Back Left Wheel
        "error" : False,
        "messages" : None
    }
    brw = { # Back Right Wheel
        "error" : False,
        "messages" : None
    }
    camera = {
        "error" : False,
        "messages" : None
    }
    arm = {
        "error" : False,
        "messages" : None
    }
    body = {
        "error" : False,
        "messages" : None
    }
    status = {
            "frontLeftWheel" : flw,
            "frontRightWheel" : frw,
            "middleLeftWheel" : mlw,
            "middleRightWheel" : mrw,
            "backLeftWheel" : blw,
            "backRightWheel" : brw,
            "camera" : camera,
            "manipulator" : arm,
            "main" : body
        }
    return status