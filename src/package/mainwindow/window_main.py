import PyQt5.QtWidgets
import PyQt5.uic

class MainWindow(PyQt5.QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        PyQt5.uic.loadUi("designer/window_main.ui", self)
        self.setWindowTitle("JARL Viking III")

def LoadMainWindow():
    wndw = MainWindow()
    wndw.show()
    return wndw