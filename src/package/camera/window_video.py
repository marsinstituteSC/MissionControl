""" Module for the creation of a window to show streamed video """

# Normal Package Imports
from configparser import ConfigParser

# PyQT5 imports, ignore pylint errors
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi

# OpenCV imports
#import numpy as np
import cv2

# Package imports
from settings import settings as cfg
from utils import warning

# Global variables for video settings
VIDEO1_LINK = None
VIDEO2_LINK = None
VIDEO1_COLOR = None
VIDEO2_COLOR = None
SETTINGS_CHANGE = False

def readFromSettings():
    """
    Reads from the settings.ini file and sets the global values
    Video link needs to be the full link in order to connect to the video source
        - ports needs to be added at the end
        - potential authentications needs to be added to the link, not implemented yet
    """
    global VIDEO1_LINK
    global VIDEO2_LINK
    global VIDEO1_COLOR
    global VIDEO2_COLOR
    global SETTINGS_CHANGE
    # Opens the settings.ini and reads from it
    try:
        config = ConfigParser()
        config.read("settings.ini")
        VIDEO1_LINK = config.get("video", "url1")
        VIDEO2_LINK = config.get("video", "url2")
        port1 = config.get("video", "port1")
        port2 = config.get("video", "port2")
        if port1:
            VIDEO1_LINK = VIDEO1_LINK + ":" + port1
        if port2:
            VIDEO2_LINK = VIDEO2_LINK + ":" + port2
        VIDEO1_COLOR = config.get("video", "color1")
        VIDEO2_COLOR = config.get("video", "color2")
        SETTINGS_CHANGE = True
    except:
        # temp error message
        print("Error occured")

class Thread(QThread):
    """Thread class to run the fetching and coverting of the video in its own thread"""

    def __init__(self, window):
        QThread.__init__(self)
        self.running = True
        self.cap1 = cv2.VideoCapture(VIDEO1_LINK)
        self.cap2 = cv2.VideoCapture(VIDEO2_LINK)
        self.switch = 0

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

    # Signals to pass the image to the corresponding slots
    changePixmap1 = pyqtSignal(QImage)
    changePixmap2 = pyqtSignal(QImage)

    def run(self):
        """Captures the video, converts them to a QImage and then passes them to the pyqt signal for the label"""
        self.play_video()
        while self.running:
            global SETTINGS_CHANGE
            if SETTINGS_CHANGE:
                self.play_video()
                SETTINGS_CHANGE = False

            # OpenCv method to read the values from the video
            ret1, frame1 = self.cap1.read()
            ret2, frame2 = self.cap2.read()

            # Checks if there were any frames from both video captures
            if ret1:
                if VIDEO1_COLOR == "True":
                    rgb_image1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
                    convert_to_qt_format1 = QImage(rgb_image1.data, rgb_image1.shape[1], rgb_image1.shape[0], QImage.Format_RGB888)
                    p1 = convert_to_qt_format1.scaled(640, 480, Qt.KeepAspectRatio)
                    self.changePixmap1.emit(p1)
                else:
                    grey_image1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
                    convert_to_qt_format1 = QImage(grey_image1.data, grey_image1.shape[1], grey_image1.shape[0], QImage.Format_Grayscale8)
                    p1 = convert_to_qt_format1.scaled(640, 480, Qt.KeepAspectRatio)
                    self.changePixmap1.emit(p1)

            if ret2:
                if VIDEO2_COLOR == "True":
                    rgb_image2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
                    convert_to_qt_format2 = QImage(rgb_image2.data, rgb_image2.shape[1], rgb_image2.shape[0], QImage.Format_RGB888)
                    p2 = convert_to_qt_format2.scaled(640, 480, Qt.KeepAspectRatio)
                    self.changePixmap2.emit(p2)
                else:
                    grey_image2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                    convert_to_qt_format2 = QImage(grey_image2.data, grey_image2.shape[1], grey_image2.shape[0], QImage.Format_Grayscale8)
                    p2 = convert_to_qt_format2.scaled(640, 480, Qt.KeepAspectRatio)
                    self.changePixmap2.emit(p2)

    def play_video(self):
        if self.switch == 1:
            self.cap1.open(VIDEO2_LINK)
            self.cap2.open(VIDEO1_LINK)
        else:
            self.cap1.open(VIDEO1_LINK)
            self.cap2.open(VIDEO2_LINK)
    
    def switch_video(self):
        if self.switch == 0:
            self.switch = 1
        else:
            self.switch = 0


class VideoWindow(QMainWindow):
    """Window class for video display"""
    def __init__(self):
        super(VideoWindow, self).__init__()
        loadUi("designer/video.ui", self)

        # Set up thread
        self.video_thread = Thread(self)
        self.video_thread.changePixmap1.connect(self.set_image1)
        self.video_thread.changePixmap2.connect(self.set_image2)

        # Toolbar button to run the video, and run the video at start
        self.actionStart_Video.triggered.connect(self.runVideo)
        self.runVideo()

        # Toolbar button to open settings
        self.actionSettings.triggered.connect(self.settings)

        # Toolbar button to video
        self.actionSwitch.triggered.connect(self.switchVideoOutput)

    @pyqtSlot(QImage)
    def set_image1(self, image):
        self.video1.setPixmap(QPixmap.fromImage(image))
        self.video1.setScaledContents(True)

    @pyqtSlot(QImage)
    def set_image2(self, image):
        self.video2.setPixmap(QPixmap.fromImage(image))
        self.video2.setScaledContents(True)

    def runVideo(self):
        self.video_thread.stop()
        self.video_thread.running = True
        self.video_thread.start()

    def settings(self):
        self.test = cfg.openSettings()

    def switchVideoOutput(self):
        self.video_thread.switch_video()

def LoadCameraWindow():
    readFromSettings()
    wndw = VideoWindow()
    wndw.show()
    return wndw