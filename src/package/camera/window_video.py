""" Module for the creation of a window to show streamed video """

# Normal Package Imports
from configparser import ConfigParser
import cProfile
import time

# PyQT5 imports, ignore pylint errors
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi

# OpenCV imports
#import numpy as np
import cv2

# Package imports
from utils import event
from settings import settings as cfg
from utils import warning

class CameraThread(QThread):
    """Thread class to run the fetching and coverting of the video in its own thread"""

    def __init__(self, window):
        super().__init__()
        # Boolean for running the loop to easily break it.
        self.running = True
        
        # Video variables
        self.videoLink1 = None
        self.color1 = None
        self.scaling1 = None
        self.videoLink2 = None
        self.color2 = None
        self.scaling2 = None
        
        # Listener for changes in settings
        cfg.SETTINGSEVENT.addListener(self, self.onSettingsChanged)

        # Initializes the capture of video
        self.cap1 = cv2.VideoCapture(self.videoLink1)
        self.cap2 = cv2.VideoCapture(self.videoLink2)

        self.loadSettings(cfg.SETTINGS)
    
    def stop(self):
        self.running = False
        self.quit()
        self.wait()
    
    def onSettingsChanged(self, name, params):
        self.loadSettings(params)

    def loadSettings(self, config):
        # Later we should check for every Video player if we choose to use 2x2 players
        # Settings for Video 1
        link1 = config.get("video", "url1") + ":" + config.get("video", "port1") if config.get("video", "port1") else config.get("video", "url1")
        c1 = config.get("video", "color1")
        res1 = config.get("video", "scaling1") if config.get("video", "scaling1") == "Source" else config.get("video", "scaling1").split("x")
        # If any changes has been made for video 1, then restart the stream
        if self.videoLink1 != link1 or self.color1 != c1 or self.scaling1 != res1:
            self.videoLink1 = link1
            self.color1 = c1
            self.scaling1 = res1
            
        # Settings for Video 2
        link2 = config.get("video", "url2") + ":" + config.get("video", "port2") if config.get("video", "port2") else config.get("video", "url2")
        c2 = config.get("video", "color2")
        res2 = config.get("video", "scaling2") if config.get("video", "scaling2") == "Source" else config.get("video", "scaling2").split("x")
        # If any changes has been made for video 2, then restart the stream
        if self.videoLink2 != link2 or self.color2 != c2 or self.scaling2 != res2:
            self.videoLink2 = link2
            self.color2 = c2
            self.scaling2 = res2
    
    # Signals to pass the image to the corresponding slots
    changePixmap1 = pyqtSignal(QPixmap)
    changePixmap2 = pyqtSignal(QPixmap)

    def drawImageFrame(self, frame, color, width = 640, height = 480):
        """Renders a single frame from the video stream and returns a pixmap"""
        try:
            colorFormat = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB if color else cv2.COLOR_BGR2GRAY)
            if width == 0 and height == 0:
                newFrame = colorFormat
            else:
                newFrame = cv2.resize(colorFormat, (width, height))
            convertToQtFormat = QImage(newFrame.data, newFrame.shape[1], newFrame.shape[0], QImage.Format_RGB888 if color else QImage.Format_Grayscale8)
            return QPixmap.fromImage(convertToQtFormat)
        except Exception as e:
            print(e)


    def run(self):
        """Captures the video, converts them to a QImage and then passes them to the pyqt signal for the label"""
        self.cap1.open(self.videoLink1)
        self.cap2.open(self.videoLink2)
        #self.pr = cProfile.Profile()
        #self.pr.enable()
        while self.running:
            try:
                # OpenCv method to read the values from the video
                ret1, frame1 = self.cap1.read()
                ret2, frame2 = self.cap2.read()

                # Checks if there were any frames from both video captures
                if ret1:
                    self.changePixmap1.emit(self.drawImageFrame(frame1, self.color1 == "True",
                    int(self.scaling1[0]) if self.scaling1 != "Source" else 0,
                    int(self.scaling1[1]) if self.scaling1 != "Source" else 0 ))

                if ret2:
                    self.changePixmap2.emit(self.drawImageFrame(frame2, self.color2 == "True",
                    int(self.scaling2[0]) if self.scaling2 != "Source" else 0,
                    int(self.scaling2[1]) if self.scaling2 != "Source" else 0 ))
            except Exception as e:
                print(e)
        #self.pr.disable()
        #self.pr.print_stats(sort='time')

class VideoWindow(QMainWindow):
    """Window class for video display"""
    def __init__(self):
        super().__init__()
        #cfg.SETTINGSEVENT.addListener(self, self.onSettingsChanged)
        #readFromSettings(cfg.SETTINGS)
        loadUi("designer/video.ui", self)

        # Set up thread
        self.video_thread = CameraThread(self)
        self.video_thread.changePixmap1.connect(self.set_image1)
        self.video_thread.changePixmap2.connect(self.set_image2)

        self.video3_widget.hide()
        self.video4_widget.hide()

        # Toolbar button to run the video, and run the video at start
        self.actionStart_Video.triggered.connect(self.runVideo)
        self.runVideo()

        # Toolbar button to open settings
        self.actionSettings.triggered.connect(self.settings)

    def onSettingsChanged(self, name, params):
        pass

    @pyqtSlot(QPixmap)
    def set_image1(self, image):
        self.video1.setPixmap(image)
        self.video1.setScaledContents(True)


    @pyqtSlot(QPixmap)
    def set_image2(self, image):
        self.video2.setPixmap(image)
        self.video2.setScaledContents(True)

    def runVideo(self):
        self.video_thread.stop()
        self.video_thread.running = True
        self.video_thread.start()

    def settings(self):
        self.setting = cfg.openSettings()

    def closeEvent(self, event):
        super().closeEvent(event)
        self.video_thread.stop()

def loadCameraWindow():
    wndw = VideoWindow()
    wndw.show()
    return wndw