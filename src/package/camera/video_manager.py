""" Manages video stream objects """

import os
import threading

from configparser import ConfigParser
from utils import warning
from settings import settings as cfg
from camera import video_threading as cam_thread_mngr
from ast import literal_eval as make_tuple

VIDEO_CONFIG = None
VIDEO_LIST = dict() # Map video stream name to video settings for that stream + active window, etc.
VIDEO_MULTI_THREAD = False # Should all streams be rendered on one thread or on their own unique threads?

def createVideoDict(src, color=0, scalingWide=0, scalingTall=0, xpos=0, ypos=0, width=0, height=0):
    return {
        "source": src,
        "color": color,
        "scaling": (scalingWide, scalingTall),
        "bounds": (xpos, ypos, width, height),
        "window": None,
    }

def getResolution(res):
    """
    Split input string, return width and height as tuple.
    """
    try:
        return make_tuple(res.lower())
    except:
        return (0, 0)

def getBounds(res):
    """
    Split input string, return width, height, xpos and ypos as tuple.
    """
    try:
        return make_tuple(res.lower())
    except:
        return (0, 0, 0, 0)

def addVideo(name, source):
    """
    Add a new video stream to the list.
    """
    global VIDEO_LIST, VIDEO_CONFIG
    if name in VIDEO_LIST:
        return False

    obj = createVideoDict(source)
    VIDEO_LIST[name] = obj
    VIDEO_CONFIG[name] = dict()
    update(name, obj)
    save()
    return True

def removeVideo(name):
    """
    Remove video stream from the list.
    """
    global VIDEO_LIST, VIDEO_CONFIG
    if name in VIDEO_LIST:
        obj = VIDEO_LIST.pop(name)
        if obj["window"]:
            obj["window"].close()
            obj["window"] = None

        if name in VIDEO_CONFIG:
            VIDEO_CONFIG.pop(name)

        save()
        return obj

    return None

def load():
    """
    Load video streams available.
    """
    global VIDEO_CONFIG, VIDEO_LIST, VIDEO_MULTI_THREAD
    VIDEO_CONFIG = ConfigParser()
    try:
        if not os.path.exists("videos.ini"):
            with open("videos.ini", "w") as configfile:
                VIDEO_CONFIG.write(configfile)
        else:
            VIDEO_CONFIG.read("videos.ini")

        for k, v in VIDEO_CONFIG.items():
            if k is "DEFAULT":
                continue

            res = getResolution(v.get("scaling", "(0,0)"))
            bounds = getBounds(v.get("bounds", "(0,0,0,0)"))
            VIDEO_LIST[k] = createVideoDict(v.get("source", ""), int(v.get("color", "0")), res[0], res[1], bounds[0], bounds[1], bounds[2], bounds[3])

        VIDEO_MULTI_THREAD = (cfg.SETTINGS.get("main", "multithread") == "True")
        cam_thread_mngr.initialize(VIDEO_MULTI_THREAD)     
    except:
        warning.showWarning("Fatal Error", "Unable to read/create videos.ini", None)

def update(id, obj):
    """
    Update video config, input actual video kv object.
    """
    global VIDEO_CONFIG
    if (obj is None) or not (id in VIDEO_CONFIG):
        return False

    VIDEO_CONFIG[id]["source"] = str(obj["source"])
    VIDEO_CONFIG[id]["color"] = str(obj["color"])
    VIDEO_CONFIG[id]["scaling"] = str(obj["scaling"])
    VIDEO_CONFIG[id]["bounds"] = str(obj["bounds"])
    return True

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
    cam_thread_mngr.THREADING_SYNC = None
    save()    
