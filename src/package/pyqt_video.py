"""Module for the creation of a window to show streamed video"""

# Normal package imports
import sys
sys.path.append("..")

# PyQT5 imports, ignore pylint errors
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi

# OpenCV imports
#import numpy as np
import cv2

# Package imports
from settings.settings import openSettings

VIDEO_LINK1 = "src/videos/demo.mp4"
VIDEO_LINK2 = "src/videos/demo2.mp4"

class Thread(QThread):
    """Thread class to run the fetching and coverting of the video in its own thread"""

    # Signals to pass the image to the corresponding slots
    changePixmap1 = pyqtSignal(QImage)
    changePixmap2 = pyqtSignal(QImage)

    def run(self):
        """Captures the video, converts them to a QImage and then passes them to the pyqt signal for the label"""

        # OpenCv capture methods
        # TODO Change the link to be a http link for the stream, let user change the video capture target
        cap1 = cv2.VideoCapture(VIDEO_LINK1)
        cap2 = cv2.VideoCapture(VIDEO_LINK2)
        
        while True:
            # OpenCv method to read the values from the video
            ret1, frame1 = cap1.read()
            ret2, frame2 = cap2.read()

            # Checks if there were any frames from both video captures
            if ret1:
                rgb_image1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
                convert_to_qt_format1 = QImage(rgb_image1.data, rgb_image1.shape[1], rgb_image1.shape[0], QImage.Format_RGB888)
                p1 = convert_to_qt_format1.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap1.emit(p1)

            if ret2:
                rgb_image2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
                convert_to_qt_format2 = QImage(rgb_image2.data, rgb_image2.shape[1], rgb_image2.shape[0], QImage.Format_RGB888)
                p2 = convert_to_qt_format2.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap2.emit(p2)


class VideoWindow(QMainWindow):
    """Window class for video display"""
    def __init__(self):
        super(VideoWindow, self).__init__()
        loadUi("src/designer/video.ui", self)
        self.video_thread = None

        # Toolbar button to run the video
        self.actionStart_Video.triggered.connect(self.runVideo)
        self.runVideo()

        # Toolbar button to open settings
        self.actionSettings.triggered.connect(self.settings)

    @pyqtSlot(QImage)
    def set_image1(self, image):
        self.video1.setPixmap(QPixmap.fromImage(image))
        self.video1.setScaledContents(True)

    @pyqtSlot(QImage)
    def set_image2(self, image):
        self.video2.setPixmap(QPixmap.fromImage(image))
        self.video2.setScaledContents(True)

    def runVideo(self):
        self.video_thread = Thread(self)
        self.video_thread.changePixmap1.connect(self.set_image1)
        self.video_thread.changePixmap2.connect(self.set_image2)
        self.video_thread.start()

    def settings(self):
        self.test = openSettings()


if __name__ == "__main__":
    APP = QApplication(sys.argv)
    WINDOW = VideoWindow()
    WINDOW.show()
    sys.exit(APP.exec_())
