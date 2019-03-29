""" Manages video stream objects """

import os
import threading

from configparser import ConfigParser
from utils import warning
from settings import settings as cfg
from camera import video_threading as cam_thread_mngr

VIDEO_CONFIG = ConfigParser()
VIDEO_LIST = dict() # Map video stream name to video settings for that stream + active window, etc.
VIDEO_MULTI_THREAD = False # Should all streams be rendered on one thread or on their own unique threads?

def createVideoDict(src, color=0, scalingWide=0, scalingTall=0):
    return {
        "source": src,
        "color": color,
        "scaling": (scalingWide, scalingTall),
        "window": None,
    }

def getResolution(res):
    """
    Split input string, return width and height as tuple.
    """
    try:
        tmp = res.lower().split("x")
        return (int(tmp[0]), int(tmp[1]))
    except:
        return (0, 0)

def addVideo(name, source):
    """
    Add a new video stream to the list.
    """
    global VIDEO_LIST
    if name in VIDEO_LIST:
        return

    VIDEO_LIST[name] = createVideoDict(source)

def removeVideo(name):
    """
    Remove video stream from the list.
    """
    global VIDEO_LIST
    if name in VIDEO_LIST:
        return VIDEO_LIST.pop(name)

    return None

def setWindowForVideo(name, obj):
    """
    Set which window to use for which video stream!
    The video thread will send its frames to the selected window.
    """
    global VIDEO_LIST
    if name in VIDEO_LIST:
        VIDEO_LIST[name]["window"] = obj

def load():
    """
    Load video streams available.
    """
    global VIDEO_CONFIG, VIDEO_LIST, VIDEO_MULTI_THREAD
    try:
        if not os.path.exists("videos.ini"):
            with open("videos.ini", "w") as configfile:
                VIDEO_CONFIG.write(configfile)
        else:
            VIDEO_CONFIG.read("videos.ini")

        for k, v in VIDEO_CONFIG.items():
            if k is "DEFAULT":
                continue

            res = getResolution(v.get("scaling", "0x0"))
            VIDEO_LIST[k] = createVideoDict(v.get("source", ""), int(v.get("color", "0")), res[0], res[1])

        VIDEO_MULTI_THREAD = (cfg.SETTINGS.get("main", "multithread") == "True")
        cam_thread_mngr.initialize(VIDEO_MULTI_THREAD)     
    except:
        warning.showWarning("Fatal Error", "Unable to read/create videos.ini", None)

def save():
    """
    Save video streams.
    """
    global VIDEO_CONFIG
    try:
        with open("videos.ini", "w") as configfile:
            VIDEO_CONFIG.write(configfile)
    except:
        warning.showWarning("Fatal Error", "Unable to write videos.ini", None)

def shutdown():
    """
    Shutdown gracefully, release all openCV stuff. 
    Tell camera windows to close.
    """    
    global VIDEO_LIST
    cam_thread_mngr.THREADING_SHUTDOWN = True
    for _, v in VIDEO_LIST.items():
        if v["window"]:
            v["window"].close()
        v["window"] = None

    VIDEO_LIST.clear()
