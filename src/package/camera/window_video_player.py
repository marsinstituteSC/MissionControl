from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, pyqtSlot, QObject
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QFileSystemModel, QTreeView
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
import sys, cv2

class VideoRenderer(QObject):
    """Simple video renderer"""
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture()
        

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("designer/videoplayer.ui", self)
        self.displayButton.clicked.connect(self.toggleVideoList)
        self.show()

    def toggleVideoList(self):
        if self.listVideos.isHidden():
            self.listVideos.show()
        else:
            self.listVideos.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VideoPlayer()
    sys.exit(app.exec_())