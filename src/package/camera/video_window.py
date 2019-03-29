""" Video Cam Stream Window """

from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, pyqtSlot, QObject
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi

from camera import video_manager as vm
from camera import video_threading as vt

class CameraStreamWindow(QMainWindow):
    def __init__(self, id, obj):
        super().__init__()
        loadUi("designer/window_video.ui", self)

        self.cameraObject = obj
        self.setWindowTitle(id)
        self.id = id
        self.thread = None # In async mode we register our own thread!
        self.recording = False
        self.btnRecord.clicked.connect(self.record)

        vt.THREADING_EVENTS.pixmap.connect(self.receiveFrame)
        vt.THREADING_EVENTS.finished.connect(self.finished)

        if vm.VIDEO_MULTI_THREAD: # Receive from specific thread.
            self.thread = None
            #self.thread.start() todo
        else: # Only receive from singular thread.            
            vt.THREADING_SYNC.add(self.id, self.cameraObject)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.cameraObject = None
        vt.THREADING_SYNC.remove(self.id)
        if not vt.THREADING_SHUTDOWN:
            vm.setWindowForVideo(self.id, None)

    def record(self):
        if vm.VIDEO_MULTI_THREAD:
            pass
        else:
            vt.THREADING_SYNC.record(self.id)

    @pyqtSlot(str)
    def finished(self, id):
        pass

    @pyqtSlot(dict)
    def receiveFrame(self, frames):
        if frames and (self.id in frames):
            self.pixmap.setPixmap(frames[self.id])

def displayVideoWindow(name):
    if not (name in vm.VIDEO_LIST):
        return

    data = vm.VIDEO_LIST[name]
    if data is None:
        return
    
    window = data["window"]
    if window is None:
        window = CameraStreamWindow(name, data)
        data["window"] = window

    window.show() if window.isHidden() else window.setWindowState(Qt.WindowActive)
    window.activateWindow()