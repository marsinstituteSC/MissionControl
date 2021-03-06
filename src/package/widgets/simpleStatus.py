from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize, Qt, pyqtSlot
from PyQt5.uic import loadUi

from utils.warning import showWarning
from utils.special_widgets import ClickableLabel

class SimpleStatus(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("designer/widget_simpleStatus.ui", self)

        # List of wheel names for easy search later
        self.wheelNames = ["top-left-wheel", "top-right-wheel", "middle-left-wheel", "middle-right-wheel", "back-left-wheel", "back-right-wheel"]
        
        # List of images used for the status widget, QIcon for scaling down images nicely
        self.statusIcons = {
            "wheelok" : QIcon("images/status icons/small_wheel_ok.png").pixmap(QSize(64,64)),
            "wheelfault" : QIcon("images/status icons/small_wheel_fault.png").pixmap(QSize(64,64)),
            "cameraok" : QIcon("images/status icons/camera_ok.png").pixmap(QSize(64,64)),
            "camerafault" : QIcon("images/status icons/camera_fault.png").pixmap(QSize(64,64)),
            "manipulatorok" : QIcon("images/status icons/manipulator_ok.png").pixmap(QSize(64,64)),
            "manipulatorfault" : QIcon("images/status icons/manipulator_fault.png").pixmap(QSize(64,64)),
            "bodyok" : QIcon("images/status icons/main_ok.png").pixmap(QSize(64,64)),
            "bodyfault" : QIcon("images/status icons/main_fault.png").pixmap(QSize(64,64))
        }
        
        # Contains the messages about the status
        self.status = {
            "top-left-wheel" : None,
            "top-right-wheel" : None,
            "middle-left-wheel" : None,
            "middle-right-wheel" : None,
            "back-left-wheel" : None,
            "back-right-wheel" : None,
            "body" : { }
        }

        self.createLabels()
        self.resetImages()

    def createLabels(self):
        """ Creates the special clickable labels and assigns them onto the grid """

        # Create layout boxes
        self.vBox_leftWheels = QVBoxLayout()
        self.vBox_rightWheels = QVBoxLayout()

        # Create wheel labels, and place them into their respectable vboxes
        self.frontLeftWheel = ClickableLabel("top-left-wheel")
        self.frontLeftWheel.clicked.connect(self.showLabelWarning)
        self.vBox_leftWheels.addWidget(self.frontLeftWheel)
        
        self.frontRightWheel = ClickableLabel("top-right-wheel")
        self.frontRightWheel.clicked.connect(self.showLabelWarning)
        self.vBox_rightWheels.addWidget(self.frontRightWheel)

        self.middleLeftWheel = ClickableLabel("middle-left-wheel")
        self.middleLeftWheel.clicked.connect(self.showLabelWarning)
        self.vBox_leftWheels.addWidget(self.middleLeftWheel)

        self.middleRightWheel = ClickableLabel("middle-right-wheel")
        self.middleRightWheel.clicked.connect(self.showLabelWarning)
        self.vBox_rightWheels.addWidget(self.middleRightWheel)

        self.backLeftWheel = ClickableLabel("back-left-wheel")
        self.backLeftWheel.clicked.connect(self.showLabelWarning)
        self.vBox_leftWheels.addWidget(self.backLeftWheel)

        self.backRightWheel = ClickableLabel("back-right-wheel")
        self.backRightWheel.clicked.connect(self.showLabelWarning)
        self.vBox_rightWheels.addWidget(self.backRightWheel)

        # Label for body
        self.main = ClickableLabel("body")
        self.main.clicked.connect(self.showLabelWarning)

        # Place the labels onto the status grid
        self.grid_status.addLayout(self.vBox_leftWheels, 0, 0)
        self.grid_status.addWidget(self.main, 0, 1, 1, 3)
        self.grid_status.addLayout(self.vBox_rightWheels, 0, 4)

    @pyqtSlot(str)
    def showLabelWarning(self,part):
        """ 
        Slot for the signals from clicking the labels 
        Display the error messages if they exist else clear the status label.
        """
        # Must check specifically for body because of the way the class stores the error messages
        if part == "body":
            text = ""
            for part, status in self.status["body"].items():
                if status:
                    for t in status:
                        # Remove trailing newline
                        text += part + " -> " + t if text == "" else "\n" + part + " -> " + t
            if text != "":
                self.label_status.setText(text)
            else:
                self.label_status.setText("")
        # Else it must be another label, which has another way of storing messages
        else:
            if self.status[part]:
                text = ""
                for txt in self.status[part]:
                    text += txt if text == "" else "\n" + txt
                self.label_status.setText(text)
            else:
                self.label_status.setText("")

    def resetImages(self):
        """ Resets or sets the images to be in its ok state """
        self.frontLeftWheel.setPixmap(self.statusIcons["wheelok"])
        self.frontRightWheel.setPixmap(self.statusIcons["wheelok"])
        self.middleLeftWheel.setPixmap(self.statusIcons["wheelok"])
        self.middleRightWheel.setPixmap(self.statusIcons["wheelok"])
        self.backLeftWheel.setPixmap(self.statusIcons["wheelok"])
        self.backRightWheel.setPixmap(self.statusIcons["wheelok"])
        self.main.setPixmap(self.statusIcons["bodyok"])

    def setWheelStatus(self, error, wheel, msg):
        """
        Changes the displayed image of the wheels, depending on the error status 
        Sets the status message if it exists onto the status storing dictionary
        """
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
        self.status[wheel] = msg if error else None 
        
    def setBodyStatus(self, error, part, msg):
        """
        Sets the status image
        Body will be affected by every error that has not a specific area in the grid, ex wheels.
        """
        # Need to add the message first in order to check if there exists an error, could be moved to the status handler
        self.status["body"][part] = msg if error else None

        # Then check if there has been a stored message, meaning there is something wrong, and set fault if there is an error.
        for _, m in self.status["body"].items():
            if m:
                self.main.setPixmap(self.statusIcons["bodyfault"])
                break
            else:
                self.main.setPixmap(self.statusIcons["bodyok"])

    def statusHandler(self, status):
        """
        Handler to set the correct image and messages from the incoming dictionary
        Will send each entry in the incoming dictionary to the correct function.
        """
        if not status:
            return

        for part, message in status.items():
            err = bool(message["error"])
            if part in self.wheelNames:
                self.setWheelStatus(err, part, message["messages"])       
            else:
                self.setBodyStatus(err, part, message["messages"])
        self.setToolTips()
        
    def setToolTips(self):
        """ Iterate through each part to create tooltips for the parts """
        # Start with the parts that has a specific label for the part.
        for part, status in self.status.items():
            text = ""
            # If there is a status message, then it means that there is an error
            # Iterate over the status message to create the tooltip text
            if status:
                for t in status:
                    text += t if text == "" else "\n" + t
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
        
        # Iterate through the body separately because of the way the data is stored
        text = ""
        for part, status in self.status["body"].items():
            if status:
                for t in status:
                    text += part + " -> " + t if text == "" else "\n" + part + " -> " + t
        self.main.setToolTip(text)
    
    def testWidget(self):
        """ Sends the example data to test the widget """
        self.statusHandler(exampleData())
                
            
def exampleData():
    """ Example data for testing purposes """
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
        "error" : True,
        "messages" : ["YEEEES"]
    }
    arm = {
        "error" : False,
        "messages" : None
    }
    mast = {
        "error" : True,
        "messages" : ["NOOOO", "YES"]
    }
    bat = {
        "error" : True,
        "messages" : ["YEEEES"]
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
            "sensormast" : mast,
            "battery" : bat
        }
    return status