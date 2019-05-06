import os
import math
import json
from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.uic import loadUi
from configparser import ConfigParser
from communications import udp_conn as UDP
from widgets import logger as log

class CustomMessageWidget(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("designer/widget_customMessage.ui", self)

        self.config = ConfigParser()
        self.config.read("messages.ini")

        # Signals:
        self.pushButton_send.clicked.connect(self.sendMessage)
        self.pushButton_addButton.clicked.connect(self.createNewMessageButton)
        self.pushButton_deleteButton.clicked.connect(self.deleteMessage)

        # Initialization
        self.checkMessagesFile()
        self.populateMessageButtons()
        self.show()

    def sendMessage(self, key=None, value=None):
        """ 
        Fetch the values in the input boxes, if no key or value is sent with the method
        else it will take the incoming key and value
        Sends the key value pair as a message to the rover 
        """
        if not (key and value):
            key = str(self.lineEdit_keyword.text())
            value = str(self.lineEdit_value.text())

        if len(key) <= 0 or len(value) <= 0:
            self.label_error.setText("Missing key or value")
            return

        self.label_error.setText("")
        UDP.ROVERSERVER.writeToRover(json.dumps({key: value}, separators=(',', ':')))
        
    def populateMessageButtons(self):
        """ Clear and populate the button box from the messages.ini in order """

        # Remove every button
        for i in reversed(range(self.gridLayout_buttons.count())): 
            self.gridLayout_buttons.itemAt(i).widget().setParent(None)
        
        sortedList = []

        # Checks if there exists any entries in the ini file
        if self.config.options("messages"):
            # Appends every item in the ini file to a list and sort them
            for key, _ in self.config.items("messages"):
                sortedList.append(key)
            sortedList.sort()

            # Create a button, in sorted order, and make the name to be the button text and connect each button to the buttonClicked method
            for key in sortedList:
                button = QPushButton()
                button.setText(key)
                button.clicked.connect(self.buttonClicked)
                # Make the buttons follow a nx3 grid, where 3 is column count and n is row count.
                self.gridLayout_buttons.addWidget(button, math.floor(self.gridLayout_buttons.count() / 3), self.gridLayout_buttons.count() % 3)
            self.frame_buttons.show()
        else:
            self.frame_buttons.hide()

    def createNewMessageButton(self):
        self.saveNewMessage()
        self.populateMessageButtons()

    def buttonClicked(self):
        """ Function for the custom buttons to send or populate it's contained information """
        # Retrieve the button that was activated to retrieve it's name (text)
        btn = self.sender()
        text = self.config.get("messages", btn.text())
        key, value = text.split("___")[0], text.split("___")[1]
        
        # Checks if the checkbox is checked for sending the message on button click or by filling out the input fields
        if self.checkBox_quickMessage.isChecked():
            self.sendMessage(key, value)
        else:
            self.lineEdit_keyword.setText(key)
            self.lineEdit_value.setText(value)
            self.lineEdit_name.setText(btn.text())

    def saveNewMessage(self):
        """ Saves the message to the ini file """
        key = self.lineEdit_keyword.text()
        value = self.lineEdit_value.text()
        name = self.lineEdit_name.text()

        if not key or not value or not name:
            self.label_error.setText("Missing key, value and/or name")
            return
        else:
            self.label_error.setText("")

        kvPair = str(key) + "___" + str(value)
        self.config.set("messages", str(name), kvPair)
        self.updateMessageFile()
    
    def deleteMessage(self):
        """
        Retrieves the name of the should be deleted button from the name input
        Deletes the button and refreshes the list if a button with the name exists
        """
        name = self.lineEdit_name.text()
        if name:
            # Delete the message if it exists, else raise a message
            if not self.config.remove_option("messages", name):
                self.label_error.setText("No button with that name")
                return
            
            # Null the line edits
            self.lineEdit_keyword.setText("")
            self.lineEdit_value.setText("")
            self.lineEdit_name.setText("")

            # Update the buttons and ini
            self.updateMessageFile()
            self.populateMessageButtons()
        else:
            self.label_error.setText("Type the name of button to delete")
            return
        self.label_error.setText("")

    def checkMessagesFile(self):
        """ Checks if the file exists, else creates one """
        try:
            if not self.config.has_section("messages"):
                self.config.add_section("messages")
            if not os.path.exists("messages.ini"):
                with open("messages.ini", "w") as configfile:
                    self.config.write(configfile)
        except Exception as e:
            log.LOGGER_EVENTS.dispatchDirectLogEvent(e, log.LOGGER_PRIORITY_ERROR)
            print(e)
    
    def updateMessageFile(self):
        """ Updates the message ini file with new information """
        # Check if the file exists and then write the new information to the file
        self.checkMessagesFile()
        try:
            with open("messages.ini", "w") as configfile:
                self.config.write(configfile)
        except Exception as e:
            log.LOGGER_EVENTS.dispatchDirectLogEvent(e, log.LOGGER_PRIORITY_ERROR)
            print(e)
