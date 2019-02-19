""" Miscellaneous Utilities """

from PyQt5.QtWidgets import QMessageBox, QDialog
from PyQt5.uic import loadUi


def showWarning(title, text, parent=None):
    msg = QMessageBox(QMessageBox.Warning, title, text, QMessageBox.Ok, parent)
    return msg.exec_()


def showPrompt(title, text, parent=None):
    msg = QMessageBox(QMessageBox.Information, title, text,
                      QMessageBox.Yes | QMessageBox.No, parent)
    return msg.exec_()
    