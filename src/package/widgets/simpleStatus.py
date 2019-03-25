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
        self.wheelNames = ["top-left-wheel", "top-right-wheel", "middle-left-wheel", "middle-right-wheel", "back-left-wheel", "back-right-wheel"]
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
            "top-left-wheel" : None,
            "top-right-wheel" : None,
            "middle-left-wheel" : None,
            "middle-right-wheel" : None,
            "back-left-wheel" : None,
            "back-right-wheel" : None,
            "camera" : None,
            "manipulator" : None,
            "body" : {
                "battery" : None,
                "sensormast" : None
                }
        }

        self.createLabels()
        self.resetImages()

    def createLabels(self):
        """ Creates the special labels and assigns them onto the grid """
        self.frontLeftWheel = ClickableLabel("top-left-wheel")
        self.frontLeftWheel.clicked.connect(self.showWarning)
        self.grid_status.addWidget(self.frontLeftWheel, 0, 0)
        
        self.frontRightWheel = ClickableLabel("top-right-wheel")
        self.frontRightWheel.clicked.connect(self.showWarning)
        self.grid_status.addWidget(self.frontRightWheel, 0, 2)

        self.middleLeftWheel = ClickableLabel("middle-left-wheel")
        self.middleLeftWheel.clicked.connect(self.showWarning)
        self.grid_status.addWidget(self.middleLeftWheel, 1, 0)

        self.middleRightWheel = ClickableLabel("middle-right-wheel")
        self.middleRightWheel.clicked.connect(self.showWarning)
        self.grid_status.addWidget(self.middleRightWheel, 1, 2)

        self.backLeftWheel = ClickableLabel("back-left-wheel")
        self.backLeftWheel.clicked.connect(self.showWarning)
        self.grid_status.addWidget(self.backLeftWheel, 2, 0)

        self.backRightWheel = ClickableLabel("back-right-wheel")
        self.backRightWheel.clicked.connect(self.showWarning)
        self.grid_status.addWidget(self.backRightWheel, 2, 2)

        grid = QGridLayout()

        self.manipulator = ClickableLabel("manipulator")
        self.manipulator.clicked.connect(self.showWarning)
        grid.addWidget(self.manipulator, 0, 0)

        self.camera = ClickableLabel("camera")
        self.camera.clicked.connect(self.showWarning)
        grid.addWidget(self.camera, 0, 1)

        self.grid_status.addLayout(grid, 0, 1)

        self.main = ClickableLabel("body")
        self.main.clicked.connect(self.showWarning)
        self.grid_status.addWidget(self.main, 1, 1, 2, 1)

    # NOTE: DO NOT STOP THE WINDOW UNDER THE ERROR FROM BEING CLICKED
    def showWarning(self, part):
        if part == "body":
            text = ""
            if self.status["body"]["battery"]:
                text += self.status["body"]["battery"] + "\n"
            elif self.status["body"]["sensormast"]:
                text += self.status["body"]["sensormast"] + "\n"
            if text != "":
                showWarning("Issues", text)
        else:
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
        if wheel == "top-left-wheel":
            self.frontLeftWheel.setPixmap(self.statusIcons["wheelfault" if error else "wheelok"])
        elif wheel == "top-right-wheel":
            self.frontRightWheel.setPixmap(self.statusIcons["wheelfault" if error else "wheelok"])
        elif wheel == "middle-left-wheel":
            self.middleLeftWheel.setPixmap(self.statusIcons["wheelfault" if error else "wheelok"])
        elif wheel == "middle-right-wheel":
            self.middleRightWheel.setPixmap(self.statusIcons["wheelfault" if error else "wheelok"])
        elif wheel == "back-left-wheel":
            self.backLeftWheel.setPixmap(self.statusIcons["wheelfault" if error else "wheelok"])
        elif wheel == "back-right-wheel":
            self.backRightWheel.setPixmap(self.statusIcons["wheelfault" if error else "wheelok"])

    def setCameraStatus(self, error):
        """ Sets the status image for the camera """
        self.camera.setPixmap(self.statusIcons["camerafault" if error else "cameraok"])

    def setManipulatorStatus(self, error):
        """ Sets the status image for the manipulator """
        self.manipulator.setPixmap(self.statusIcons["manipulatorfault" if error else "manipulatorok"])
        
    def setBodyStatus(self, part, error, msg):
        """
        Sets the status image
        Body will be affected by every error that has not a specific area in the grid, ex wheels.
        """
        if part == "battery":
            self.status["body"]["battery"] = msg
        elif part == "sensormast":
            self.status["body"]["sensormast"] = msg
        if self.status["body"]["sensormast"] or self.status["body"]["battery"]:
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
            err = bool(message["error"])
            
            if part in self.wheelNames:
                self.setWheelStatus(err, part)                
            elif part == "camera":
                self.setCameraStatus(err)
            elif part == "manipulator":
                self.setManipulatorStatus(err)
            elif part == "battery" or part == "sensormast":
                self.setBodyStatus(part, err, message["messages"])
            else:
                continue

            self.status[part] = message["messages"] if err else None
        self.setToolTips()
        
    def setToolTips(self):
        for part, status in self.status.items():
            text = ""
            if status:
                for t in status:
                    text += t + "\n"
            if part == "top-left-wheel":
                self.frontLeftWheel.setToolTip(text)
            elif part == "top-right-wheel":
                self.frontRightWheel.setToolTip(text)
            elif part == "middle-left-wheel":
                self.middleLeftWheel.setToolTip(text)
            elif part == "middle-right-wheel":
                self.middleRightWheel.setToolTip(text)
            elif part == "back-left-wheel":
                self.backLeftWheel.setToolTip(text)
            elif part == "back-right-wheel":
                self.backRightWheel.setToolTip(text)
            elif part == "camera":
                self.camera.setToolTip(text)
            elif part == "manipulator":
                self.manipulator.setToolTip(text)
        if self.status["body"]["sensormast"] and self.status["body"]["battery"]:
            self.main.setToolTip(self.status["body"]["sensormast"][0] + " " + self.status["body"]["battery"][0])
        elif self.status["body"]["sensormast"] and not self.status["body"]["battery"]:
            self.main.setToolTip(self.status["body"]["sensormast"][0])
        elif not self.status["body"]["sensormast"] and self.status["body"]["battery"]:
            self.main.setToolTip(self.status["body"]["battery"][0])
    
    def testWidget(self):
        self.statusHandler(exampleData())
                
            
def exampleData():
    flw = {
        "error" : True,
        "messages" : ["ERROR"]
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
    mast = {
        "error" : True,
        "messages" : ["NOOOO"]
    }
    status = {
            "top-left-wheel" : flw,
            "top-right-wheel" : frw,
            "middle-left-wheel" : mlw,
            "middle-right-wheel" : mrw,
            "back-left-wheel" : blw,
            "back-right-wheel" : brw,
            "camera" : camera,
            "manipulator" : arm,
            "sensormast" : mast
        }
    return status