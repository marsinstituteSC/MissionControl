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

class VideoRendering(QObject):
    def __init__(self, videoNr):
        super().__init__()
        self.running = True
        
        # Video settings
        self.videoUrl = None
        self.videoScaling = None
        self.videoColor = None
        self.videoNumber = videoNr # Used to identify from where settings should be read, color and scale. Should not be changed
        self.sourceNumber = videoNr # Used to identify from where source url should be read from settings, to allow multiple of same video with different settings.
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
        link = config.get("video", "url" + str(self.sourceNumber)) + ":" + config.get("video", "port" + str(self.sourceNumber)) if config.get("video", "port" + str(self.sourceNumber)) else config.get("video", "url" + str(self.sourceNumber))
        color = (config.get("video", "color" + str(self.videoNumber)) == "True")
        scaling = config.get("video", "scaling" + str(self.videoNumber))
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

        self.video1Name = None
        self.video2Name = None
        self.video3Name = None
        self.video4Name = None

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

        # Toolbar buttons
        self.actionStart_Video.triggered.connect(self.restartAllVideos)
        self.actionSettings.triggered.connect(self.settings)

        # Combobox signals
        self.video1_choice.currentIndexChanged.connect(self.changeVideo1)
        self.video2_choice.currentIndexChanged.connect(self.changeVideo2)
        self.video3_choice.currentIndexChanged.connect(self.changeVideo3)
        self.video4_choice.currentIndexChanged.connect(self.changeVideo4)

        self.loadSettings(cfg.SETTINGS)

        # Start threads if they are enabled and hides the widgets that are not enabled
        if self.enabled1 : self.thread1.start()
        if self.enabled2 : self.thread2.start()
        if self.enabled3 : self.thread3.start()
        if self.enabled4 : self.thread4.start()
        
        
    def changeVideo1(self, i):
        self.video1.sourceNumber = i+1
        self.video1.loadSettings(cfg.SETTINGS)
        self.restartSpecificVideo(1, True)
    def changeVideo2(self, i):
        self.video2.sourceNumber = i+1
        self.video2.loadSettings(cfg.SETTINGS)
        self.restartSpecificVideo(2, True)
    def changeVideo3(self, i):
        self.video3.sourceNumber = i+1
        self.video3.loadSettings(cfg.SETTINGS)
        self.restartSpecificVideo(3, True)
    def changeVideo4(self, i):
        self.video4.sourceNumber = i+1
        self.video4.loadSettings(cfg.SETTINGS)
        self.restartSpecificVideo(4, True)

    def onSettingsChanged(self, name, params):
        self.loadSettings(params)

    def loadSettings(self, config):
        """
        Loads the settings and needs to do:
            - If enabled is false for a video, stop the thread and video
            - If enabled is true for a video, restart the video
        """
        if self.video1Name != config.get("video", "name1") or self.video2Name != config.get("video", "name2") or self.video3Name != config.get("video", "name3") or self.video4Name != config.get("video", "name4"):
            self.video1Name = config.get("video", "name1")
            self.video2Name = config.get("video", "name2")
            self.video3Name = config.get("video", "name3")
            self.video4Name = config.get("video", "name4")
            # Populate every combobox/drop-down menu
            self.populateComboBox()

        # Checks if there has been a change in enable, if so then show and run video or hide and stop video.
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

        # If both video players at the bottom or top are the only ones active, disable the top frame in order to get a video on each row
        if self.enabled2 and self.enabled4 and not self.enabled1 and not self.enabled3:
            self.frame.hide()
            self.gridLayout_2.removeWidget(self.video4_widget) # Doesn't seem like we need to call this, but its here just in case.
            self.gridLayout_2.addWidget(self.video4_widget, 1, 0)
        elif self.enabled1 and self.enabled3 and not self.enabled2 and not self.enabled4:
            self.frame_2.hide()
            self.gridLayout.removeWidget(self.video3_widget)
            self.gridLayout.addWidget(self.video3_widget, 1, 0)
        elif self.enabled1 and not self.enabled2 and not self.enabled3 and not self.enabled4:
            self.frame_2.hide()
        elif self.enabled2 and not self.enabled1 and not self.enabled3 and not self.enabled4:
            self.frame.hide()
        elif self.enabled3 and not self.enabled2 and not self.enabled1 and not self.enabled4:
            self.frame_2.hide()
        elif self.enabled4 and not self.enabled2 and not self.enabled3 and not self.enabled1:
            self.frame.hide()
        else:
            self.gridLayout.removeWidget(self.video3_widget)
            self.gridLayout.addWidget(self.video3_widget, 0, 1)
            self.gridLayout_2.removeWidget(self.video4_widget)
            self.gridLayout_2.addWidget(self.video4_widget, 0, 1)
            self.frame.show()
            self.frame_2.show()


    @pyqtSlot(QPixmap)
    def set_image1(self, image):
        self.video1_player.setPixmap(image)

    @pyqtSlot(QPixmap)
    def set_image2(self, image):
        self.video2_player.setPixmap(image)

    @pyqtSlot(QPixmap)
    def set_image3(self, image):
        self.video3_player.setPixmap(image)

    @pyqtSlot(QPixmap)
    def set_image4(self, image):
        self.video4_player.setPixmap(image)

    def restartAllVideos(self):
        """
        Restarts every video thread and object by setting each objects running to false and pauses the thread.
        Then restarts the thread and running.
        """
        self.restartSpecificVideo(1, True)
        self.restartSpecificVideo(2, True)
        self.restartSpecificVideo(3, True)
        self.restartSpecificVideo(4, True)

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

    def populateComboBox(self):
        self.video1_choice.clear()
        self.video1_choice.addItem(self.video1Name)
        self.video1_choice.addItem(self.video2Name)
        self.video1_choice.addItem(self.video3Name)
        self.video1_choice.addItem(self.video4Name)
        self.video1_choice.setCurrentIndex(self.video1_choice.findText(self.video1Name))

        self.video2_choice.clear()
        self.video2_choice.addItem(self.video1Name)
        self.video2_choice.addItem(self.video2Name)
        self.video2_choice.addItem(self.video3Name)
        self.video2_choice.addItem(self.video4Name)
        self.video2_choice.setCurrentIndex(self.video2_choice.findText(self.video2Name))

        self.video3_choice.clear()
        self.video3_choice.addItem(self.video1Name)
        self.video3_choice.addItem(self.video2Name)
        self.video3_choice.addItem(self.video3Name)
        self.video3_choice.addItem(self.video4Name)
        self.video3_choice.setCurrentIndex(self.video3_choice.findText(self.video3Name))

        self.video4_choice.clear()
        self.video4_choice.addItem(self.video1Name)
        self.video4_choice.addItem(self.video2Name)
        self.video4_choice.addItem(self.video3Name)
        self.video4_choice.addItem(self.video4Name)
        self.video4_choice.setCurrentIndex(self.video4_choice.findText(self.video4Name))

    def settings(self):
        self.setting = cfg.openSettings()

    def closeEvent(self, event):
        super().closeEvent(event)
        self.thread1.exit()
        self.thread2.exit()
        self.thread3.exit()
        self.thread4.exit()

def loadCameraWindow():
    wndw = VideoWindow()
    wndw.show()
    return wndw