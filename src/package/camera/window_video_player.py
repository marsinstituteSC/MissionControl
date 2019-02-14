from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, pyqtSlot, QObject
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QFileSystemModel, QTreeView
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
import sys

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("designer/videoplayer.ui", self)
        self.model = QFileSystemModel()
        self.model.setRootPath("videos")
        self.treeView.setModel(self.model)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VideoPlayer()
    sys.exit(app.exec_())