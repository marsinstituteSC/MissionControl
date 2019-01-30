""" Establishes a UDP connection with the Rover, implements methods for sending & receiving data! """

import PyQt5.QtCore
import PyQt5.QtNetwork
import time
import queue

from utils import event

SERVERHOST = None # 192.168.1.3
SERVERPORT = None

CLIENTHOST = None
CLIENTPORT = None

ROVERSERVER = None # Allow other files/pgks to easily access our udp server through this global.
TICK = (50 / 1000) # How often in msec should we check inc / send outgoing msgs.
SETTINGS_CHANGED = False # Force update for connection

# Reads from the settings.ini and sets the server address and client address
def readFromSettings(config):
    global SERVERHOST
    global SERVERPORT
    global CLIENTHOST
    global CLIENTPORT
    global SETTINGS_CHANGED

    # If any of these are changed, then we need to reconnect to the server, client port is read inside the loop so it is fine
    if SERVERHOST != config.get("main", "serveraddress") or SERVERPORT != int(config.get("main", "serverport")) or CLIENTHOST != config.get("main", "clientaddress"):
        SERVERHOST = config.get("main", "serveraddress")
        SERVERPORT = int(config.get("main", "serverport"))
        CLIENTHOST = config.get("main", "clientaddress")
        SETTINGS_CHANGED = True
    
    CLIENTPORT = int(config.get("main", "clientport"))


class UDPRoverServer(PyQt5.QtCore.QThread, event.EventListener):
    def __init__(self):
        super().__init__()
        self.messagesToSend = queue.Queue()
        self.connect()

    # !!! This has been defined later, is it this one you want or the other one !!!
    #def __del__(self):
     #   pass

    def onEvent(self, e):
        """Handle settings changed event"""
        pass

    def connect(self):
        self.serverAddress = PyQt5.QtNetwork.QHostAddress(SERVERHOST)
        self.clientAddress = PyQt5.QtNetwork.QHostAddress(CLIENTHOST)
        self.socket = PyQt5.QtNetwork.QUdpSocket(self)
        self.socket.bind(self.clientAddress, CLIENTPORT)

    def writeToRover(self, data):
        self.messagesToSend.put_nowait(data)

    def fetchMessageToSend(self):
        try:
             return self.messagesToSend.get_nowait()
        except: # Raises an exception if empty.
            return ''

    def __del__(self):
        self.wait() 

    def run(self):
        global SETTINGS_CHANGED
        while True:
            if SETTINGS_CHANGED:
                self.connect()
                SETTINGS_CHANGED = False
            
            if self.socket.hasPendingDatagrams():
                data, _, _ = self.socket.readDatagram(self.socket.pendingDatagramSize())
                if data is not None: # TODO Process incoming messages
                    print(data.decode())                    

            # Fetch messages from a thread-safe queue, if empty, skip and wait
            # for TICK time.
            d = self.fetchMessageToSend()
            if d:
                self.socket.writeDatagram(d.encode(), self.serverAddress, SERVERPORT)    

            time.sleep(TICK)

def connectToRoverServer():
    global ROVERSERVER
    conn = UDPRoverServer()
    conn.start()
    ROVERSERVER = conn
    return conn