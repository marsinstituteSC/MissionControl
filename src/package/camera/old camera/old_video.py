""" Module for the creation of a window to show streamed video """

# Normal Package Imports
from configparser import ConfigParser
import cProfile
import time

# PyQT5 imports, ignore pylint errors
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, pyqtSlot, QObject
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

class VideoRendering(QObject):
    def __init__(self, videoNr):
        super().__init__()
        self.running = True
        
        # Video settings
        self.videoUrl = None
        self.videoScaling = None
        self.videoColor = None
        self.videoNumber = videoNr
        self.cap = cv2.VideoCapture(self.videoUrl)

        # Settings listener
        cfg.SETTINGSEVENT.addListener(self, self.onSettingsChanged)

        self.loadSettings(cfg.SETTINGS)

    changePixmap = pyqtSignal(QPixmap)

    def run(self):
        self.cap.open(self.videoUrl)
        while self.running:
            try:
                ret, frame = self.cap.read()
                if ret:
                    colorFormat = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB if self.videoColor else cv2.COLOR_BGR2GRAY)
                    if self.videoScaling == "Source":
                        newFrame = colorFormat
                    else:
                        width, height = self.videoScaling.split("x")
                        newFrame = cv2.resize(colorFormat, (int(width), int(height)))
                    convertToQtFormat = QImage(newFrame.data, newFrame.shape[1], newFrame.shape[0], QImage.Format_RGB888 if self.videoColor else QImage.Format_Grayscale8)
                    self.changePixmap.emit(QPixmap.fromImage(convertToQtFormat))
            except Exception as e:
                print(e)

    def onSettingsChanged(self, name, params):
        self.loadSettings(params)

    def loadSettings(self, config):
        # Corresponds to video widget number.
        link = config.get("video", "url" + str(self.videoNumber)) + ":" + config.get("video", "port" + str(self.videoNumber)) if config.get("video", "port" + str(self.videoNumber)) else config.get("video", "url" + str(self.videoNumber))
        color = (config.get("video", "color" + str(self.videoNumber)) == "True")
        scaling = config.get("video", "scaling" + str(self.videoNumber)) if config.get("video", "scaling" + str(self.videoNumber)) == "Source" else config.get("video", "scaling" + str(self.videoNumber))
        # If any changes has been made for video 1, then restart the stream
        if self.videoUrl != link or self.videoColor != scaling or self.videoScaling != scaling:
            self.videoUrl = link
            self.videoColor = color
            self.videoScaling = scaling

    
class VideoWindow(QMainWindow):
    """Window class for video display"""
    def __init__(self):
        super().__init__()
        cfg.SETTINGSEVENT.addListener(self, self.onSettingsChanged)
        
        loadUi("designer/video.ui", self)

        # Set up thread
        #self.video_thread = CameraThread(self)
        #self.video_thread.changePixmap1.connect(self.set_image1)
        #self.video_thread.changePixmap2.connect(self.set_image2)

        # Initializes threads
        self.thread1 = QThread()
        self.thread2 = QThread()
        self.thread3 = QThread()
        self.thread4 = QThread()

        # Initializes enabled
        self.enabled1 = True
        self.enabled2 = True
        self.enabled3 = True
        self.enabled4 = True

        # Initialize video rendering objects and place them into threads
        self.video1 = VideoRendering(1)
        self.video1.changePixmap.connect(self.set_image1)
        self.video1.moveToThread(self.thread1)
        self.thread1.started.connect(self.video1.run)

        self.video2 = VideoRendering(2)
        self.video2.changePixmap.connect(self.set_image2)
        self.video2.moveToThread(self.thread2)
        self.thread2.started.connect(self.video2.run)

        self.video3 = VideoRendering(3)
        self.video3.changePixmap.connect(self.set_image3)
        self.video3.moveToThread(self.thread3)
        self.thread3.started.connect(self.video3.run)

        self.video4 = VideoRendering(4)
        self.video4.changePixmap.connect(self.set_image4)
        self.video4.moveToThread(self.thread4)
        self.thread4.started.connect(self.video4.run)

        # Toolbar button to run the video, and run the video at start
        self.actionStart_Video.triggered.connect(self.restartAllVideos)

        # Toolbar button to open settings
        self.actionSettings.triggered.connect(self.settings)

        self.loadSettings(cfg.SETTINGS)

        # Start threads if they are enabled and hides the widgets that are not enabled
        self.thread1.start() if self.enabled1 else self.video1_widget.hide()
        self.thread2.start() if self.enabled2 else self.video2_widget.hide()
        self.thread3.start() if self.enabled3 else self.video3_widget.hide()
        self.thread4.start() if self.enabled4 else self.video4_widget.hide()
        
        # Resize every widget
        

    def onSettingsChanged(self, name, params):
        self.loadSettings(params)

    def loadSettings(self, config):
        """
        Loads the settings and needs to do:
            - If enabled is false for a video, stop the thread and video
            - If enabled is true for a video, restart the video
        """
        # Only write if there has been a change
        if self.enabled1 != (config.get("video", "enable1") == "True"):
            self.enabled1 = (config.get("video", "enable1") == "True")
            if self.enabled1:
                self.restartSpecificVideo(1, True)
                self.video1_widget.show()
            else:
                self.restartSpecificVideo(1, False)
                self.video1_widget.hide()

        if self.enabled2 != (config.get("video", "enable2") == "True"):
            self.enabled2 = (config.get("video", "enable2") == "True")
            if self.enabled2:
                self.restartSpecificVideo(2, True)
                self.video2_widget.show()
            else:
                self.restartSpecificVideo(2, False)
                self.video2_widget.hide()
        
        if self.enabled3 != (config.get("video", "enable3") == "True"):
            self.enabled3 = (config.get("video", "enable3") == "True")
            if self.enabled3:
                self.restartSpecificVideo(3, True)
                self.video3_widget.show()
            else:
                self.restartSpecificVideo(3, False)
                self.video3_widget.hide()
        
        if self.enabled4 != (config.get("video", "enable4") == "True"):
            self.enabled4 = (config.get("video", "enable4") == "True")
            if self.enabled4:
                self.restartSpecificVideo(4, True)
                self.video4_widget.show()
            else:
                self.restartSpecificVideo(4, False)
                self.video4_widget.hide()

    @pyqtSlot(QPixmap)
    def set_image1(self, image):
        self.video1_player.setPixmap(image)
        self.video1_player.setScaledContents(True)

    @pyqtSlot(QPixmap)
    def set_image2(self, image):
        self.video2_player.setPixmap(image)
        self.video2_player.setScaledContents(True)

    @pyqtSlot(QPixmap)
    def set_image3(self, image):
        self.video3_player.setPixmap(image)
        self.video3_player.setScaledContents(True)

    @pyqtSlot(QPixmap)
    def set_image4(self, image):
        self.video4_player.setPixmap(image)
        self.video4_player.setScaledContents(True)

    def restartAllVideos(self):
        """
        Restarts every video thread and object by setting each objects running to false and pauses the thread.
        Then restarts the thread and running.
        """
        self.restartSpecificVideo(1, True)
        self.restartSpecificVideo(2, True)
        self.restartSpecificVideo(3, True)
        self.restartSpecificVideo(4, True)
        #self.video_thread.stop()
        #self.video_thread.running = True
        #self.video_thread.start()

    def restartSpecificVideo(self, videoNumber, restart):
        """
        Restarts the specific video, if it is enabled
        Inputs:
            - videoNumber, identifier for the video for this to restart/stop, 1-4
            - restart, if true then the video should restart, if else it will only stop
        """
        if videoNumber == 1 and self.enabled1 == True:
            self.video1.running = False
            self.thread1.quit()
            self.thread1.wait()
            if restart:
                self.video1.running = True
                self.thread1.start()
        elif videoNumber == 2 and self.enabled2 == True:
            self.video2.running = False
            self.thread2.quit()
            self.thread2.wait()
            if restart:
                self.video2.running = True
                self.thread2.start()
        elif videoNumber == 3 and self.enabled3 == True:
            self.video3.running = False
            self.thread3.quit()
            self.thread3.wait()
            if restart:
                self.video3.running = True
                self.thread3.start()
        elif videoNumber == 4 and self.enabled4 == True:
            self.video4.running = False
            self.thread4.quit()
            self.thread4.wait()
            if restart:
                self.video4.running = True
                self.thread4.start()

    def settings(self):
        self.setting = cfg.openSettings()

    def closeEvent(self, event):
        super().closeEvent(event)

def loadCameraWindow():
    wndw = VideoWindow()
    wndw.show()
    return wndw