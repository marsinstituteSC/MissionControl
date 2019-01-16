import sys
import PyQt5.QtWidgets
from mainwindow import window_main as wm

if __name__ == "__main__":
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    mainwnd = wm.LoadMainWindow()   
    sys.exit(app.exec_())
