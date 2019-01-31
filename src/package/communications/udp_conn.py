""" Establishes a UDP connection with the Rover, implements methods for sending & receiving data! """

import PyQt5.QtCore
import PyQt5.QtNetwork
import time
import queue

from utils import event
from settings import settings as cfg

# 192.168.1.3 <- actual server addr. to use.

CLIENTHOST = PyQt5.QtNetwork.QHostAddress("127.0.0.1")
CLIENTPORT = 37500

ROVERSERVER = None # Allow other files/pgks to easily access our udp server through this global.
TICK = (50 / 1000) # How often in msec should we check inc / send outgoing msgs.

class UDPRoverServer(PyQt5.QtCore.QThread):
    def __init__(self):
        super().__init__()
        cfg.SETTINGSEVENT.addListener(self, self.onSettingsChanged)
        self.loadSettings(cfg.SETTINGS)
        self.messagesToSend = queue.Queue()        
        self.connect()

    def connect(self):
        self.socket = PyQt5.QtNetwork.QUdpSocket(self)
        self.socket.bind(CLIENTHOST, CLIENTPORT)

    def writeToRover(self, data):
        self.messagesToSend.put_nowait(data)

    def fetchMessageToSend(self):
        try:
             return self.messagesToSend.get_nowait()
        except: # Raises an exception if empty.
            return ''

    def onSettingsChanged(self, name, params):
        self.loadSettings(params)

    def loadSettings(self, config):
        # IF client socket must be changed, disconnect old socket first, however changing the client socket is unnecessary as it uses the localhost address anyways.
        #if self.socket.connected(): # Disconnect socket, unbind properly first.
        #self.socket.disconnectFromHost()
        self.serverAddress = config.get("main", "serveraddress")
        self.serverPort = int(config.get("main", "serverport"))
        

    def __del__(self):
        global ROVERSERVER
        cfg.SETTINGSEVENT.removeListener(self)
        self.wait() 
        ROVERSERVER = None

    def run(self):
        while True:            
            if self.socket.hasPendingDatagrams():
                data, _, _ = self.socket.readDatagram(self.socket.pendingDatagramSize())
                if data is not None: # TODO Process incoming messages
                    print(data.decode())                    

            # Fetch messages from a thread-safe queue, if empty, skip and wait
            # for TICK time.
            d = self.fetchMessageToSend()
            if d:
                self.socket.writeDatagram(d.encode(), self.serverAddress, self.serverPort)    

            time.sleep(TICK)

def connectToRoverServer():
    global ROVERSERVER
    conn = UDPRoverServer()
    conn.start()
    ROVERSERVER = conn
    return conn