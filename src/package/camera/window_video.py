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

class VideoRenderingSync(QObject):
    """
    Class to render all four videos
    """
    def __init__(self):
        super().__init__()
        self.running = True

        # Initialize every local video settings
        self.videoUrl1 = None
        self.videoColor1 = None
        self.videoScaling1 = None
        self.videoUrl2 = None
        self.videoColor2 = None
        self.videoScaling2 = None
        self.videoUrl3 = None
        self.videoColor3 = None
        self.videoScaling3 = None
        self.videoUrl4 = None
        self.videoColor4 = None
        self.videoScaling4 = None

        # Initialize temporary variables and sourcenumber
        self.sourceNumber1 = 1
        self.videoUrlTemp1 = None
        self.videoColorTemp1 = None
        self.videoScalingTemp1 = None
        self.sourceNumber2 = 2
        self.videoUrlTemp2 = None
        self.videoColorTemp2 = None
        self.videoScalingTemp2 = None
        self.sourceNumber3 = 3
        self.videoUrlTemp3 = None
        self.videoColorTemp3 = None
        self.videoScalingTemp3 = None
        self.sourceNumber4 = 4
        self.videoUrlTemp4 = None
        self.videoColorTemp4 = None
        self.videoScalingTemp4 = None
        self.changed = False

        # In order to disable a specific video, use enabled to check
        self.enabled1 = True
        self.enabled2 = True
        self.enabled3 = True
        self.enabled4 = True

        # Initialize capture
        self.cap1 = cv2.VideoCapture(self.videoUrl1)
        self.cap2 = cv2.VideoCapture(self.videoUrl2)
        self.cap3 = cv2.VideoCapture(self.videoUrl3)
        self.cap4 = cv2.VideoCapture(self.videoUrl4)

        cfg.SETTINGSEVENT.addListener(self, self.onSettingsChanged)
        self.loadSettings(cfg.SETTINGS)

    changePixmap = pyqtSignal(dict)

    def run(self):
        self.setNewSettings()
        self.cap1.open(self.videoUrl1)
        self.cap2.open(self.videoUrl2)
        self.cap3.open(self.videoUrl3)
        self.cap4.open(self.videoUrl4)
        while self.running:
            try:
                # This is to only apply settings when a new iteration of the loop starts.
                if self.changed:
                    self.setNewSettings()
                    self.changed = False
                # Dictionary with every pixmap to send a single signal when everyone is done rendering
                output = {
                    1 : None,
                    2 : None,
                    3 : None,
                    4 : None
                }
                ret1, frame1 = self.cap1.read()
                ret2, frame2 = self.cap2.read()
                ret3, frame3 = self.cap3.read()
                ret4, frame4 = self.cap4.read()
                if ret1 or ret2 or ret3 or ret4:
                    if ret1 and self.enabled1:
                        colorFormat = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB if self.videoColor1 else cv2.COLOR_BGR2GRAY)
                        if self.videoScaling1 == "Source":
                            newFrame = colorFormat
                        else:
                            # Check if it will scale the image down or up and use InterArea Interpolation for downscale and InterLinear for upscale.
                            width, height = self.videoScaling1.split("x")
                            newFrame = cv2.resize(colorFormat, (int(width), int(height)))
                        qtFormat = QImage(newFrame.data, newFrame.shape[1], newFrame.shape[0], QImage.Format_RGB888 if self.videoColor1 else QImage.Format_Grayscale8)
                        output[1] = QPixmap.fromImage(qtFormat)
                    else:
                        self.cap1.release()

                    if ret2 and self.enabled2:
                        colorFormat = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB if self.videoColor2 else cv2.COLOR_BGR2GRAY)
                        if self.videoScaling2 == "Source":
                            newFrame = colorFormat
                        else:
                            # Check if it will scale the image down or up and use InterArea Interpolation for downscale and InterLinear for upscale.
                            width, height = self.videoScaling2.split("x")
                            newFrame = cv2.resize(colorFormat, (int(width), int(height)))
                        qtFormat = QImage(newFrame.data, newFrame.shape[1], newFrame.shape[0], QImage.Format_RGB888 if self.videoColor2 else QImage.Format_Grayscale8)
                        output[2] = QPixmap.fromImage(qtFormat)
                    else:
                        self.cap2.release()

                    if ret3 and self.enabled3:
                        colorFormat = cv2.cvtColor(frame3, cv2.COLOR_BGR2RGB if self.videoColor3 else cv2.COLOR_BGR2GRAY)
                        if self.videoScaling3 == "Source":
                            newFrame = colorFormat
                        else:
                            # Check if it will scale the image down or up and use InterArea Interpolation for downscale and InterLinear for upscale.
                            width, height = self.videoScaling3.split("x")
                            newFrame = cv2.resize(colorFormat, (int(width), int(height)))
                        qtFormat = QImage(newFrame.data, newFrame.shape[1], newFrame.shape[0], QImage.Format_RGB888 if self.videoColor3 else QImage.Format_Grayscale8)
                        output[3] = QPixmap.fromImage(qtFormat)
                    else:
                        self.cap3.release()

                    if ret4 and self.enabled4:
                        colorFormat = cv2.cvtColor(frame4, cv2.COLOR_BGR2RGB if self.videoColor4 else cv2.COLOR_BGR2GRAY)
                        if self.videoScaling4 == "Source":
                            newFrame = colorFormat
                        else:
                            # Check if it will scale the image down or up and use InterArea Interpolation for downscale and InterLinear for upscale.
                            width, height = self.videoScaling4.split("x")
                            newFrame = cv2.resize(colorFormat, (int(width), int(height)))
                        qtFormat = QImage(newFrame.data, newFrame.shape[1], newFrame.shape[0], QImage.Format_RGB888 if self.videoColor4 else QImage.Format_Grayscale8)
                        output[4] = QPixmap.fromImage(qtFormat)
                    else:
                        self.cap4.release()
                    self.changePixmap.emit(output)
                else:
                    self.running = False
                    self.cap1.release()
                    self.cap2.release()
                    self.cap3.release()
                    self.cap4.release()
            except Exception as e:
                print(e)

    def onSettingsChanged(self, name, params):
        self.loadSettings(params)

    def loadSettings(self, config):
        link = config.get("video", "url" + str(self.sourceNumber1)) + ":" + config.get("video", "port" + str(self.sourceNumber1)) if config.get("video", "port" + str(self.sourceNumber1)) else config.get("video", "url" + str(self.sourceNumber1))
        color = (config.get("video", "color1") == "True")
        scaling = config.get("video", "scaling1")
        self.enabled1 = (config.get("video", "enable1") == "True")
        if self.videoUrlTemp1 != link or self.videoColorTemp1 != scaling or self.videoScalingTemp1 != scaling:
            # Temporary values to hold new settings
            self.videoUrlTemp1 = link
            self.videoColorTemp1 = color
            self.videoScalingTemp1 = scaling
            self.changed = True
        link = config.get("video", "url" + str(self.sourceNumber2)) + ":" + config.get("video", "port" + str(self.sourceNumber2)) if config.get("video", "port" + str(self.sourceNumber2)) else config.get("video", "url" + str(self.sourceNumber2))
        color = (config.get("video", "color2") == "True")
        scaling = config.get("video", "scaling2")
        self.enabled2 = (config.get("video", "enable2") == "True")
        if self.videoUrlTemp2 != link or self.videoColorTemp2 != scaling or self.videoScalingTemp2 != scaling:
            # Temporary values to hold new settings
            self.videoUrlTemp2 = link
            self.videoColorTemp2 = color
            self.videoScalingTemp2 = scaling
            self.changed = True
        link = config.get("video", "url" + str(self.sourceNumber3)) + ":" + config.get("video", "port" + str(self.sourceNumber3)) if config.get("video", "port" + str(self.sourceNumber3)) else config.get("video", "url" + str(self.sourceNumber3))
        color = (config.get("video", "color3") == "True")
        scaling = config.get("video", "scaling3")
        self.enabled3 = (config.get("video", "enable3") == "True")
        if self.videoUrlTemp3 != link or self.videoColorTemp3 != scaling or self.videoScalingTemp3 != scaling:
            # Temporary values to hold new settings
            self.videoUrlTemp3 = link
            self.videoColorTemp3 = color
            self.videoScalingTemp3 = scaling
            self.changed = True
        link = config.get("video", "url" + str(self.sourceNumber4)) + ":" + config.get("video", "port" + str(self.sourceNumber4)) if config.get("video", "port" + str(self.sourceNumber4)) else config.get("video", "url" + str(self.sourceNumber4))
        color = (config.get("video", "color4") == "True")
        scaling = config.get("video", "scaling4")
        self.enabled4 = (config.get("video", "enable4") == "True")
        if self.videoUrlTemp4 != link or self.videoColorTemp4 != scaling or self.videoScalingTemp4 != scaling:
            # Temporary values to hold new settings
            self.videoUrlTemp4 = link
            self.videoColorTemp4 = color
            self.videoScalingTemp4 = scaling
            self.changed = True

    def setNewSettings(self):
        self.videoUrl1 = self.videoUrlTemp1
        self.videoColor1 = self.videoColorTemp1
        self.videoScaling1 = self.videoScalingTemp1
        self.videoUrl2 = self.videoUrlTemp2
        self.videoColor2 = self.videoColorTemp2
        self.videoScaling2 = self.videoScalingTemp2
        self.videoUrl3 = self.videoUrlTemp3
        self.videoColor3 = self.videoColorTemp3
        self.videoScaling3 = self.videoScalingTemp3
        self.videoUrl4 = self.videoUrlTemp4
        self.videoColor4 = self.videoColorTemp4
        self.videoScaling4 = self.videoScalingTemp4

class VideoRenderingAsync(QObject):
    """
    Class to render a single video source
    Inputs:
        - videoNr, Identifier for where in the settings file, video + 1, video + 2 etc, it should look for settings and video source.
    Output:
        - None. But contains a changePixmap signal anyone can listen to.
    """
    def __init__(self, videoNr):
        super().__init__()
        self.running = True

        self.videoUrlTemp = None
        self.videoColorTemp = None
        self.videoScalingTemp = None
        
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
        self.videoUrl = self.videoUrlTemp
        self.videoColor = self.videoColorTemp
        self.videoScaling = self.videoScalingTemp
        self.cap.open(self.videoUrl)
        while self.running:
            try:
                # This is to only apply settings when a new iteration of the loop starts.
                self.videoUrl = self.videoUrlTemp
                self.videoColor = self.videoColorTemp
                self.videoScaling = self.videoScalingTemp
                ret, frame = self.cap.read()
                if ret:
                    colorFormat = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB if self.videoColor else cv2.COLOR_BGR2GRAY)
                    if self.videoScaling == "Source":
                        newFrame = colorFormat
                    else:
                        # Check if it will scale the image down or up and use InterArea Interpolation for downscale and InterLinear for upscale.
                        width, height = self.videoScaling.split("x")
                        newFrame = cv2.resize(colorFormat, (int(width), int(height)))
                    convertToQtFormat = QImage(newFrame.data, newFrame.shape[1], newFrame.shape[0], QImage.Format_RGB888 if self.videoColor else QImage.Format_Grayscale8)
                    self.changePixmap.emit(QPixmap.fromImage(convertToQtFormat))
                else:
                    self.running = False
                    self.cap.release()
            except Exception as e:
                print(e)
        

    def onSettingsChanged(self, name, params):
        self.loadSettings(params)

    def loadSettings(self, config):
        link = config.get("video", "url" + str(self.sourceNumber)) + ":" + config.get("video", "port" + str(self.sourceNumber)) if config.get("video", "port" + str(self.sourceNumber)) else config.get("video", "url" + str(self.sourceNumber))
        color = (config.get("video", "color" + str(self.videoNumber)) == "True")
        scaling = config.get("video", "scaling" + str(self.videoNumber))
        if self.videoUrlTemp != link or self.videoColorTemp != scaling or self.videoScalingTemp != scaling:
            # Temporary values to hold new settings
            self.videoUrlTemp = link
            self.videoColorTemp = color
            self.videoScalingTemp = scaling

class VideoWindow(QMainWindow):
    """Window class for video display"""
    def __init__(self):
        super().__init__()
        cfg.SETTINGSEVENT.addListener(self, self.onSettingsChanged)   
        loadUi("designer/video.ui", self)
        self.threadMode = "Sync" if cfg.SETTINGS.get("main", "threadmode") == "True" else "Async"

        self.enabled1 = True
        self.enabled2 = True
        self.enabled3 = True
        self.enabled4 = True

        self.video1Name = None
        self.video2Name = None
        self.video3Name = None
        self.video4Name = None

        # Toolbar buttons
        self.actionStart_Video.triggered.connect(self.restartAllVideos)
        self.actionSettings.triggered.connect(self.settings)

        # Combobox signals
        self.video1_choice.currentIndexChanged.connect(self.changeVideo1)
        self.video2_choice.currentIndexChanged.connect(self.changeVideo2)
        self.video3_choice.currentIndexChanged.connect(self.changeVideo3)
        self.video4_choice.currentIndexChanged.connect(self.changeVideo4)

        # Only start one thread and place every renderer into that thread
        if self.threadMode == "Sync":
            self.thread = QThread()
            self.video = VideoRenderingSync()
            self.video.moveToThread(self.thread)
            self.thread.started.connect(self.video.run)
            self.video.changePixmap.connect(self.set_all_images)
        # Start 4 threads and move each renderer into each own thread
        else:
            # Initialize the video rendering class and connect the signal to the slot
            self.video1 = VideoRenderingAsync(1)
            self.video1.changePixmap.connect(self.set_image1)
            self.video2 = VideoRenderingAsync(2)
            self.video2.changePixmap.connect(self.set_image2)
            self.video3 = VideoRenderingAsync(3)
            self.video3.changePixmap.connect(self.set_image3)
            self.video4 = VideoRenderingAsync(4)
            self.video4.changePixmap.connect(self.set_image4)
            self.thread1 = QThread()
            self.thread2 = QThread()
            self.thread3 = QThread()
            self.thread4 = QThread()
            self.video1.moveToThread(self.thread1)
            self.video2.moveToThread(self.thread2)
            self.video3.moveToThread(self.thread3)
            self.video4.moveToThread(self.thread4)
            self.thread1.started.connect(self.video1.run)
            self.thread2.started.connect(self.video2.run)
            self.thread3.started.connect(self.video3.run)
            self.thread4.started.connect(self.video4.run)
        
        self.loadSettings(cfg.SETTINGS)
        # Start threads if they are enabled
        if self.threadMode == "Sync":
            self.thread.start()
        else:
            if self.enabled1 : self.thread1.start()
            if self.enabled2 : self.thread2.start()
            if self.enabled3 : self.thread3.start()
            if self.enabled4 : self.thread4.start()

 
    def changeVideo1(self, i):
        if i != -1:
            if self.threadMode == "Sync":
                self.video.sourceNumber1 = i+1
                self.video.loadSettings(cfg.SETTINGS)
                self.restartAllVideos()
            else:
                self.video1.sourceNumber = i+1
                self.video1.loadSettings(cfg.SETTINGS)
                self.restartSpecificVideo(1, True)
    def changeVideo2(self, i):
        if i != -1:
            if self.threadMode == "Sync":
                self.video.sourceNumber2 = i+1
                self.video.loadSettings(cfg.SETTINGS)
                self.restartAllVideos()
            else:
                self.video2.sourceNumber = i+1
                self.video2.loadSettings(cfg.SETTINGS)
                self.restartSpecificVideo(2, True)
    def changeVideo3(self, i):
        if i != -1:
            if self.threadMode == "Sync":
                self.video.sourceNumber3 = i+1
                self.video.loadSettings(cfg.SETTINGS)
                self.restartAllVideos()
            else:
                self.video3.sourceNumber = i+1
                self.video3.loadSettings(cfg.SETTINGS)
                self.restartSpecificVideo(3, True)
    def changeVideo4(self, i):
        if i != -1:
            if self.threadMode == "Sync":
                self.video.sourceNumber4 = i+1
                self.video.loadSettings(cfg.SETTINGS)
                self.restartAllVideos()
            else:
                self.video4.sourceNumber = i+1
                self.video4.loadSettings(cfg.SETTINGS)
                self.restartSpecificVideo(4, True)

    def onSettingsChanged(self, name, params):
        self.loadSettings(params)

    def loadSettings(self, config):
        """
        Loads the settings and needs to do:
            - Populate the drop down boxes for each video
            - If enabled is false for a video, stop the thread and video
            - If enabled is true for a video, restart the video
        """
        #self.pr = cProfile.Profile()
        #self.pr.enable()
        
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

        """
        First check if the two videos on the bottom or top is active if so:
            - Hide the empty frame and move one of the widgets
        Check if it is only one video enabled and hide the empty widget to get fullscreen.
        Otherwise reset the layout
        """
        if self.enabled2 and self.enabled4 and not self.enabled1 and not self.enabled3:
            # Move video 2 top the top and video 4 to the bottom
            print("TEST")
            self.gridLayout.removeWidget(self.video1_widget)
            self.gridLayout.removeWidget(self.video2_widget)
            self.gridLayout.removeWidget(self.video3_widget)
            self.gridLayout.removeWidget(self.video4_widget)
            self.gridLayout.addWidget(self.video2_widget, 0, 0)
            self.gridLayout.addWidget(self.video4_widget, 1, 0)
        elif self.enabled1 and self.enabled3 and not self.enabled2 and not self.enabled4:
            # Move video 1 top the top and video 3 to the bottom
            self.gridLayout.removeWidget(self.video1_widget)
            self.gridLayout.removeWidget(self.video2_widget)
            self.gridLayout.removeWidget(self.video3_widget)
            self.gridLayout.removeWidget(self.video4_widget)
            self.gridLayout.addWidget(self.video1_widget, 0, 0)
            self.gridLayout.addWidget(self.video3_widget, 1, 0)
        # If only one video is displayed on the top row or bottom row
        elif self.enabled1 and not self.enabled3 and self.enabled2 and self.enabled4:
            self.gridLayout.removeWidget(self.video1_widget)
            self.gridLayout.removeWidget(self.video2_widget)
            self.gridLayout.removeWidget(self.video3_widget)
            self.gridLayout.removeWidget(self.video4_widget)
            self.gridLayout.addWidget(self.video1_widget, 0, 0, 1, 2)
            self.gridLayout.addWidget(self.video2_widget, 1, 0)
            self.gridLayout.addWidget(self.video4_widget, 1, 1)
        elif self.enabled3 and not self.enabled1 and self.enabled2 and self.enabled4:
            self.gridLayout.removeWidget(self.video1_widget)
            self.gridLayout.removeWidget(self.video2_widget)
            self.gridLayout.removeWidget(self.video3_widget)
            self.gridLayout.removeWidget(self.video4_widget)
            self.gridLayout.addWidget(self.video3_widget, 0, 0, 1, 2)
            self.gridLayout.addWidget(self.video2_widget, 1, 0)
            self.gridLayout.addWidget(self.video4_widget, 1, 1)
        elif self.enabled2 and not self.enabled4 and self.enabled1 and self.enabled3:
            self.gridLayout.removeWidget(self.video1_widget)
            self.gridLayout.removeWidget(self.video2_widget)
            self.gridLayout.removeWidget(self.video3_widget)
            self.gridLayout.removeWidget(self.video4_widget)
            self.gridLayout.addWidget(self.video2_widget, 1, 0, 1, 2)
            self.gridLayout.addWidget(self.video1_widget, 0, 0)
            self.gridLayout.addWidget(self.video3_widget, 0, 1)
        elif self.enabled4 and not self.enabled2 and self.enabled1 and self.enabled3:
            self.gridLayout.removeWidget(self.video1_widget)
            self.gridLayout.removeWidget(self.video2_widget)
            self.gridLayout.removeWidget(self.video3_widget)
            self.gridLayout.removeWidget(self.video4_widget)
            self.gridLayout.addWidget(self.video4_widget, 1, 0, 1, 2)
            self.gridLayout.addWidget(self.video1_widget, 0, 0)
            self.gridLayout.addWidget(self.video3_widget, 0, 1)
        else:
            self.gridLayout.removeWidget(self.video1_widget)
            self.gridLayout.removeWidget(self.video2_widget)
            self.gridLayout.removeWidget(self.video3_widget)
            self.gridLayout.removeWidget(self.video4_widget)
            self.gridLayout.addWidget(self.video1_widget, 0, 0)
            self.gridLayout.addWidget(self.video2_widget, 1, 0)
            self.gridLayout.addWidget(self.video3_widget, 0, 1)
            self.gridLayout.addWidget(self.video4_widget, 1, 1)
        #self.pr.disable()
        #self.pr.print_stats(sort='time')
    
    # Draw the image to the labels with the rendered image
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
    @pyqtSlot(dict)
    def set_all_images(self, images):
        if images[1]:
            self.video1_player.setPixmap(images[1])
        if images[2]:
            self.video2_player.setPixmap(images[2])
        if images[3]:
            self.video3_player.setPixmap(images[3])
        if images[4]:
            self.video4_player.setPixmap(images[4])

    def restartAllVideos(self):
        """
        Restarts every video thread and object by setting each objects running to false and pauses the thread.
        Then restarts the thread and running.
        """
        if self.threadMode == "Sync":
            self.video.running = False
            self.thread.quit()
            self.thread.wait()
            self.video.running = True
            self.thread.start()
        else:    
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
        self.video1_choice.currentIndexChanged.disconnect(self.changeVideo1)
        self.video1_choice.clear()
        self.video1_choice.addItem(self.video1Name)
        self.video1_choice.addItem(self.video2Name)
        self.video1_choice.addItem(self.video3Name)
        self.video1_choice.addItem(self.video4Name)
        self.video1_choice.setCurrentIndex(self.video1_choice.findText(self.video1Name))
        self.video1_choice.currentIndexChanged.connect(self.changeVideo1)

        self.video2_choice.currentIndexChanged.disconnect(self.changeVideo2)
        self.video2_choice.clear()
        self.video2_choice.addItem(self.video1Name)
        self.video2_choice.addItem(self.video2Name)
        self.video2_choice.addItem(self.video3Name)
        self.video2_choice.addItem(self.video4Name)
        self.video2_choice.setCurrentIndex(self.video2_choice.findText(self.video2Name))
        self.video2_choice.currentIndexChanged.connect(self.changeVideo2)

        self.video3_choice.currentIndexChanged.disconnect(self.changeVideo3)
        self.video3_choice.clear()
        self.video3_choice.addItem(self.video1Name)
        self.video3_choice.addItem(self.video2Name)
        self.video3_choice.addItem(self.video3Name)
        self.video3_choice.addItem(self.video4Name)
        self.video3_choice.setCurrentIndex(self.video3_choice.findText(self.video3Name))
        self.video3_choice.currentIndexChanged.connect(self.changeVideo3)

        self.video4_choice.currentIndexChanged.disconnect(self.changeVideo4)
        self.video4_choice.clear()
        self.video4_choice.addItem(self.video1Name)
        self.video4_choice.addItem(self.video2Name)
        self.video4_choice.addItem(self.video3Name)
        self.video4_choice.addItem(self.video4Name)
        self.video4_choice.setCurrentIndex(self.video4_choice.findText(self.video4Name))
        self.video4_choice.currentIndexChanged.connect(self.changeVideo4)

    def settings(self):
        self.setting = cfg.openSettings()

    def closeEvent(self, event):
        super().closeEvent(event)
        if self.threadMode == "Sync":
            self.thread.exit()
        else:
            self.thread1.exit()
            self.thread2.exit()
            self.thread3.exit()
            self.thread4.exit()
        event.accept()

def loadCameraWindow():
    wndw = VideoWindow()
    wndw.show()
    return wndw