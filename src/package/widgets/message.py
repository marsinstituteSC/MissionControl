from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.uic import loadUi
import sys, random, time, os, math
from configparser import ConfigParser

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

        self.checkMessagesFile()
        self.populateMessageButtons()
        self.show()

    def sendMessage(self, key = None, value = None):
        """ Sends the key value pair as a message to the rover """
        if not key or not value:
            key = str(self.lineEdit_keyword.text())
            value = str(self.lineEdit_value.text())
            if not key or not value:
                self.label_error.setText("Missing key or value")
                return
        self.label_error.setText("")
        
        # TODO: Send to rover
        

    def populateMessageButtons(self):
        """ Clear and populate the button box from the messages.ini """

        for i in reversed(range(self.gridLayout_buttons.count())): 
            self.gridLayout_buttons.itemAt(i).widget().setParent(None)
        
        sortedList = []

        if self.config.options("messages"):
            for key, _ in self.config.items("messages"):
                sortedList.append(key)
            sortedList.sort()

            for key in sortedList:
                button = QPushButton()
                button.setText(key)
                button.clicked.connect(self.buttonClicked)
                self.gridLayout_buttons.addWidget(button, math.floor(self.gridLayout_buttons.count() / 3), self.gridLayout_buttons.count() % 3)
            self.frame_buttons.show()
        else:
            self.frame_buttons.hide()

    def createNewMessageButton(self):
        self.saveNewMessage()
        self.populateMessageButtons()

    def buttonClicked(self):
        btn = self.sender()
        text = self.config.get("messages", btn.text())
        key, value = text.split("___")[0], text.split("___")[1]
        if self.checkBox_quickMessage.isChecked():
            self.sendMessage(key, value)
        else:
            self.lineEdit_keyword.setText(key)
            self.lineEdit_value.setText(value)
            self.lineEdit_name.setText(btn.text())

    def saveNewMessage(self):
        """ Saves the message """
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
            print(e)
    
    def updateMessageFile(self):
        """ Updates the message ini file with new information """
        # Check if the file exists and then write the new information to the file
        self.checkMessagesFile()
        try:
            with open("messages.ini", "w") as configfile:
                self.config.write(configfile)
        except Exception as e:
            print(e)