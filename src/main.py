""" Default Application Entry Point """

import sys
import PyQt5.QtWidgets

from camera import window_video as wv
from communications import udp_conn
from controller import gamepad as gp
from mainwindow import window_main as wm

if __name__ == "__main__":    
    conn = udp_conn.ConnectToRoverServer()
    xbox = gp.LoadGamepad()
    app = PyQt5.QtWidgets.QApplication(sys.argv)    
    mainwnd = wm.LoadMainWindow()  
    camwnd = wv.LoadCameraWindow()
    sys.exit(app.exec_())
