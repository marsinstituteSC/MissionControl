""" Miscellaneous Utilities """

from PyQt5.QtWidgets import QMessageBox

def showWarning(title, text, parent = None):
    msg = QMessageBox(QMessageBox.Warning, title, text, QMessageBox.Ok, parent)
    return msg.exec_()