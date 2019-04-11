""" 
Manages threading, streaming and such for video streams,
uses openCV for rendering.
"""

import time
import threading
import cv2
import datetime
import os

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QObject, Qt
from PyQt5.QtGui import QImage, QPixmap
from camera import video_manager as vm
from camera import video_window as vw

class CameraEvents(QObject):
    pixmap = pyqtSignal(dict) # Send a dict of pixmaps.
    finished = pyqtSignal(str) # Which video finished.

    def __init__(self):
        super().__init__()

    def dispatchPixmapEvent(self, v):
        self.pixmap.emit(v)

    def dispatchFinishedEvent(self, v):
        self.finished.emit(str(v))

THREADING_EVENTS = CameraEvents()
THREADING_SUSPEND_TIME = 1.0 # How long to wait during inactivity? (prevent thread starvation)
THREADING_SHUTDOWN = False
THREADING_SYNC = None

class CameraStreamObject(QObject):
    def __init__(self, id, obj):
        super().__init__()
        self.id = id
        self.obj = obj
        self.stream = None
        self.finished = False
        self.rec = False
        self.recorder = None
        self.refresh = False

    def __del__(self):
        self.closeStream()

    def openStream(self):
        """
        Create or re-create the openCV stream.
        """
        try:
            if self.stream:
                self.stream.release()

            self.finished = False
            self.stream = cv2.VideoCapture(None)
            return self.stream.open(self.obj["source"])            
        except Exception as e:
            print(e)
            return False

    def closeStream(self):
        """
        Close OpenCV stream.
        """
        res = False
        try:
            if self.stream:
                self.stream.release()

            if self.recorder:
                self.recorder.release()

            res = True
        except Exception as e:
            print(e)
        finally:
            self.stream = None
            self.recorder = None
            return res

    def finish(self):
        """
        Stream is closed/finished.
        """
        self.finished = True
        self.closeStream()
        THREADING_EVENTS.dispatchFinishedEvent(self.id)    

    def createVideoForRecording(self):
        """
        Create recorder object, folder path + file!
        """
        try:
            time = datetime.datetime.now()        
            vid = "videos/{}-{}-{}/{}_{}-{}-{}.avi".format(
                str(time.day), 
                str(time.month), 
                str(time.year),
                self.id.replace(" ", "-").lower(),
                str(time.hour),
                str(time.minute),
                str(time.second)
                )
            directory = os.path.dirname(vid)

            if not os.path.exists(directory):
                os.makedirs(directory)

            return cv2.VideoWriter(vid, cv2.VideoWriter_fourcc('M','J','P','G'), 60, (int(self.stream.get(3)), int(self.stream.get(4))))
        except Exception as e:
            print(e)
            return None

    def recording(self, frame):
        """
        Record video, if so desired. Cleanup when done!!!
        """
        if self.rec:
            if self.recorder is None:
                self.recorder = self.createVideoForRecording()
            if self.recorder:
                self.recorder.write(frame)
        elif self.recorder: # Recording is off but we were recording, release!
            self.recorder.release()
            self.recorder = None

    def render(self):
        """
        Render one frame, return the result frame.
        """
        # If user wants to refresh, clear capture obj.
        if self.refresh:
            if self.stream:
                self.stream.release()
            self.stream = None
            self.refresh = False
            self.finished = False
            
        # Finished or no source? Don't care.
        if self.finished or (len(self.obj["source"]) <= 0):
            return None

        # Try to open the stream, if it fails, close and try again 'later'.
        if (self.stream is None) and not self.openStream():
            self.closeStream()
            return None

        result = None
        try:
            color = self.obj["color"]
            scale = self.obj["scaling"]   
            ret, frame = self.stream.read()
            if ret:
                self.recording(frame)
                finishedFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB if (color == 0) else cv2.COLOR_BGR2GRAY)
                if scale[0] > 0 and scale[1] > 0: # Check if it will scale the image down or up and use InterArea Interpolation for downscale and InterLinear for upscale.
                    finishedFrame = cv2.resize(finishedFrame, scale)   

                result = QPixmap.fromImage(QImage(finishedFrame.data, finishedFrame.shape[1], finishedFrame.shape[0], QImage.Format_RGB888 if (color == 0) else QImage.Format_Grayscale8))
            else:
                self.finish()
        except Exception as e:
            print(e)
        finally:
            return result

class CameraSync(QObject):
    def __init__(self):
        super().__init__()
        self.shutdown = False  
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.run)
        self.thread.start()
        self.items = dict()
        self.lock = threading.Lock()

    def __del__(self):
        self.shutdown = True
        if not self.thread.wait(100):
            self.thread.terminate()
        self.thread = None

    def add(self, id, obj):
        with self.lock:
            self.items[id] = CameraStreamObject(id, obj)

    def remove(self, id):
        with self.lock:
            if id in self.items:
                obj = self.items.pop(id)
                obj.closeStream()

    def record(self, id):
        with self.lock:        
            if id in self.items:
                self.items[id].rec = not self.items[id].rec

    def refresh(self, id):
        with self.lock:        
            if id in self.items:
                self.items[id].refresh = True

    def run(self):
        global THREADING_SHUTDOWN, THREADING_EVENTS, THREADING_SUSPEND_TIME
        frames = dict()
        while not THREADING_SHUTDOWN and not self.shutdown:
            with self.lock:
                for id, obj in self.items.items():
                    frame = obj.render()
                    if frame:
                        frames[id] = frame

            # Send pixmap to ui thread, suspend otherwise, if nothing else to do!
            THREADING_EVENTS.dispatchPixmapEvent(frames.copy()) if len(frames) > 0 else time.sleep(THREADING_SUSPEND_TIME) 
            frames.clear()
        self.items.clear()

def initialize(val):
    """
    Determine threading mode!
    """
    global THREADING_SYNC, THREADING_SHUTDOWN
    THREADING_SHUTDOWN = False
    THREADING_SYNC = (CameraSync() if (not val) else None)
    
