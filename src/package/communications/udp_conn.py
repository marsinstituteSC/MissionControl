""" Establishes a UDP connection with the Rover, implements methods for sending & receiving data! """

import time
import queue

from PyQt5.QtCore import QThread
from PyQt5.QtNetwork import QUdpSocket, QHostAddress, QNetworkInterface

from utils import event
from settings import settings as cfg

# 192.168.1.3 <- actual server addr. to use.

CLIENTHOST = QHostAddress("127.0.0.1")
CLIENTPORT = 37500

SENSOR_PUBLISH_SERVER = QHostAddress("239.255.43.21")
SENSOR_PUBLISH_PORT = 45454

ROVERSERVER = None # Allow other files/pgks to easily access our udp server through this global.
TICK = (50 / 1000) # How often in msec should we check inc / send outgoing msgs.

class UDPRoverServer(QThread):
    def __init__(self):
        super().__init__()
        cfg.SETTINGSEVENT.addListener(self, self.onSettingsChanged)
        self.shouldDestroy = False
        self.loadSettings(cfg.SETTINGS)
        self.messagesToSend = queue.Queue()        
        self.connectToGamepadServer()
        self.connectToSensorPublisher()

    def connectToGamepadServer(self):
        self.gamepadSocket = QUdpSocket(self)
        self.gamepadSocket.bind(CLIENTHOST, CLIENTPORT)

    def connectToSensorPublisher(self):
        self.sensorpubSocket = QUdpSocket(self)
        self.sensorpubSocket.bind(QHostAddress.AnyIPv4, SENSOR_PUBLISH_PORT, QUdpSocket.ShareAddress)
        self.sensorpubSocket.joinMulticastGroup(SENSOR_PUBLISH_SERVER)

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
        self.serverAddress = config.get("main", "serveraddress")
        self.serverPort = int(config.get("main", "serverport"))        

    def destroy(self):
        self.shouldDestroy = True
        self.gamepadSocket.close()
        self.sensorpubSocket.leaveMulticastGroup(SENSOR_PUBLISH_SERVER)
        self.sensorpubSocket.close()

    def run(self):
        while self.shouldDestroy == False:
            if self.gamepadSocket.hasPendingDatagrams():
                data, _, _ = self.gamepadSocket.readDatagram(self.gamepadSocket.pendingDatagramSize())
                if data is not None: # TODO Process incoming messages
                    print(data.decode())                    

            if self.sensorpubSocket.hasPendingDatagrams():
                data, _, _ = self.sensorpubSocket.readDatagram(self.sensorpubSocket.pendingDatagramSize())
                if data is not None:
                    print("Received Sensor Data:", data.decode())

            # Fetch messages from a thread-safe queue, if empty, skip and wait
            # for TICK time.
            d = self.fetchMessageToSend()
            if d:
                self.gamepadSocket.writeDatagram(d.encode(), self.serverAddress, self.serverPort)    

            time.sleep(TICK)        

def connectToRoverServer():
    global ROVERSERVER
    ROVERSERVER = UDPRoverServer()
    ROVERSERVER.start()
    return ROVERSERVER

def disconnectFromRoverServer():
    global ROVERSERVER
    if ROVERSERVER is None:
        return

    ROVERSERVER.destroy()
    ROVERSERVER = None
    
