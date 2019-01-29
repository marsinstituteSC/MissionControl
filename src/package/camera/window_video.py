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
VIDEO1_RESOLUTION = "1080"
VIDEO2_RESOLUTION = "1080"
SETTINGS_CHANGE = False

def readFromSettings(config):
    """
    Reads from the settings.ini file and sets the global values
    Video link needs to be the full link in order to connect to the video source
        - ports needs to be added at the end
        - potential authentications needs to be added to the link, not implemented yet
    """
    # Global Variables
    global VIDEO1_LINK
    global VIDEO2_LINK
    global VIDEO1_COLOR
    global VIDEO2_COLOR
    global SETTINGS_CHANGE
    global VIDEO1_RESOLUTION
    global VIDEO2_RESOLUTION

    # Video Link Creation
    VIDEO1_LINK = config.get("video", "url1")
    VIDEO2_LINK = config.get("video", "url2")
    port1 = config.get("video", "port1")
    port2 = config.get("video", "port2")
    if port1:
        VIDEO1_LINK = VIDEO1_LINK + ":" + port1
    if port2:
        VIDEO2_LINK = VIDEO2_LINK + ":" + port2
    
    # Video Color
    VIDEO1_COLOR = config.get("video", "color1")
    VIDEO2_COLOR = config.get("video", "color2")
    
    # Video Resolution
    res1 = config.get("video", "resolution1").split("x")
    res2 = config.get("video", "resolution1").split("x")
    VIDEO1_RESOLUTION = res1
    VIDEO2_RESOLUTION = res2

    # Global setting to force change in video stream.
    SETTINGS_CHANGE = True

class CameraThread(QThread):
    """Thread class to run the fetching and coverting of the video in its own thread"""

    def __init__(self, window):
        super().__init__()
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

    def drawImageFrame(self, frame, color, width = 640, height = 480):
        """Renders a single frame from the video stream"""
        colorFormat = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB if color else cv2.COLOR_BGR2GRAY)
        convertToQtFormat = QImage(colorFormat.data, colorFormat.shape[1], colorFormat.shape[0], QImage.Format_RGB888 if color else QImage.Format_Grayscale8)
        return convertToQtFormat.scaled(width, height, Qt.KeepAspectRatio)

    def run(self):
        """Captures the video, converts them to a QImage and then passes them to the pyqt signal for the label"""
        self.play_video()
        while self.running:
            global SETTINGS_CHANGE
            global VIDEO1_RESOLUTION
            global VIDEO2_RESOLUTION
            if SETTINGS_CHANGE:
                self.play_video()
                SETTINGS_CHANGE = False

            # OpenCv method to read the values from the video
            ret1, frame1 = self.cap1.read()
            ret2, frame2 = self.cap2.read()

            # Checks if there were any frames from both video captures

            if ret1:
                self.changePixmap1.emit(self.drawImageFrame(frame1, VIDEO1_COLOR == "True", int(VIDEO1_RESOLUTION[0]), int(VIDEO1_RESOLUTION[1])))

            if ret2:
                self.changePixmap2.emit(self.drawImageFrame(frame2, VIDEO2_COLOR == "True", int(VIDEO2_RESOLUTION[0]), int(VIDEO2_RESOLUTION[1])))            

    def play_video(self):
        self.cap1.open(VIDEO2_LINK if self.switch == 1 else VIDEO1_LINK)
        self.cap2.open(VIDEO1_LINK if self.switch == 1 else VIDEO2_LINK)
    
    def switch_video(self):
        self.switch = not self.switch
        global SETTINGS_CHANGE
        SETTINGS_CHANGE = True

class VideoWindow(QMainWindow):
    """Window class for video display"""
    def __init__(self):
        super().__init__()
        loadUi("designer/video.ui", self)

        # Set up thread
        self.video_thread = CameraThread(self)
        self.video_thread.changePixmap1.connect(self.set_image1)
        self.video_thread.changePixmap2.connect(self.set_image2)

        # Toolbar button to run the video, and run the video at start
        self.actionStart_Video.triggered.connect(self.runVideo)
        self.runVideo()

        # Toolbar button to open settings
        self.actionSettings.triggered.connect(self.settings)

        # Toolbar button to video
        self.actionSwitch.triggered.connect(self.video_thread.switch_video)

    @pyqtSlot(QImage)
    def set_image1(self, image):
        self.video1.renderPixmap(QPixmap.fromImage(image))
        #self.video1.setScaledContents(True)

    @pyqtSlot(QImage)
    def set_image2(self, image):
        self.video2.renderPixmap(QPixmap.fromImage(image))
        #self.video2.setScaledContents(True)

    def runVideo(self):
        self.video_thread.stop()
        self.video_thread.running = True
        self.video_thread.start()

    def settings(self):
        self.setting = cfg.openSettings()

def loadCameraWindow():
    wndw = VideoWindow()
    wndw.show()
    return wndw