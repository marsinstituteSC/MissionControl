""" Miscellaneous Utilities """

from PyQt5.QtWidgets import QMessageBox

def ShowWarning(parent, title, text):
    msg = QMessageBox(QMessageBox.Warning, title, text, QMessageBox.Ok, parent)
    return msg.exec_()