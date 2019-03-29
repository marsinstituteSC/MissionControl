""" Video Cam Stream Window """

from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, pyqtSlot, QObject, QRect, QPoint
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi

from camera import video_manager as vm
from camera import video_threading as vt
from utils.math import clamp

class CameraStreamWindow(QMainWindow):
    def __init__(self, id, obj):
        super().__init__()
        loadUi("designer/window_video.ui", self)

        self.cameraObject = obj
        self.setWindowTitle(id)
        self.id = id
        self.recording = False

        self.btnUpdate.clicked.connect(self.update)
        self.btnRecord.clicked.connect(self.record)
        self.colorChoices.currentIndexChanged.connect(self.propertyChange)
        self.scaleChoices.currentIndexChanged.connect(self.propertyChange)
        self.btnToggleFunctions.clicked.connect(self.toggleFunctions)

        vt.THREADING_EVENTS.pixmap.connect(self.receiveFrame)
        vt.THREADING_EVENTS.finished.connect(self.finished)

        self.syncObject = (vt.CameraSync() if vm.VIDEO_MULTI_THREAD else vt.THREADING_SYNC)
        self.syncObject.add(self.id, self.cameraObject)

        # Set properties
        bounds = obj["bounds"]
        color = obj["color"]
        scaling = obj["scaling"]
        src = obj["source"]
        
        if scaling[0] > 0 and scaling[1] > 0:
            comboScaleItems = [self.scaleChoices.itemText(i) for i in range(self.scaleChoices.count())]
            for idx, val in enumerate(comboScaleItems):
                if val.lower() == "{}x{}".format(scaling[0], scaling[1]):
                    self.scaleChoices.setCurrentIndex(idx)
                    break

        self.sourceField.setText(src)
        self.colorChoices.setCurrentIndex(clamp(color, 0, (self.colorChoices.count() - 1)))

        # Update proportions
        if bounds[2] > 0 and bounds[3] > 0:
            self.resize(bounds[2], bounds[3])
            self.move(bounds[0], bounds[1])
        
        self.groupFunctions.hide()

    def closeEvent(self, event):        
        self.cameraObject["bounds"] = (self.pos().x(), self.pos().y(), self.size().width(), self.size().height())
        vm.update(self.id, self.cameraObject)       
        
        self.syncObject.remove(self.id)
        self.syncObject = None
        self.cameraObject = None
        if not vt.THREADING_SHUTDOWN:
            vm.setWindowForVideo(self.id, None)

        super().closeEvent(event)

    def record(self):
        self.recording = not self.recording
        self.btnRecord.setText("Stop Recording" if self.recording else "Start Recording")
        self.syncObject.record(self.id)
            
    def propertyChange(self):
        """
        Triggered whenever color or scaling is changed!
        """
        scale = self.scaleChoices.currentText().lower().split("x")
        self.cameraObject["color"] = self.colorChoices.currentIndex()
        self.cameraObject["scaling"] = vm.getResolution("({},{})".format(scale[0], scale[1])) if len(scale) >= 2 else (0, 0) 

    def update(self):
        """
        Tell threading to update source and other stuff if needed!
        """
        self.cameraObject["source"] = self.sourceField.text()
        self.syncObject.refresh(self.id)

    @pyqtSlot(str)
    def finished(self, id):
        if self.id == id:
            self.recording = False
            self.btnRecord.setText("Start Recording")

    @pyqtSlot(dict)
    def receiveFrame(self, frames):
        if frames and (self.id in frames):
            self.pixmap.setPixmap(frames[self.id])

    def toggleFunctions(self):
        """ Toggle to show/hide video functions, record will be unaffected """
        if self.groupFunctions.isHidden():
            self.groupFunctions.show()
            self.btnToggleFunctions.setText("Hide Functions")
        else:
            self.groupFunctions.hide()
            self.btnToggleFunctions.setText("Show Functions")

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

def displayAllVideoWindows():
    for k, _ in vm.VIDEO_LIST.items():
        displayVideoWindow(k)
