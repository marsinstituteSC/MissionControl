""" Establishes a UDP connection with the Rover, implements methods for sending & receiving data! """

import time
import queue
import json
import datetime

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtNetwork import QUdpSocket, QHostAddress, QNetworkInterface

from utils import event
from settings import settings as cfg
from communications import database

# 192.168.1.3 <- actual server addr. to use.

ROVERSERVER = None # Allow other files/pgks to easily access our udp server through this global.
TICK = (50 / 1000) # How often in msec should we check inc / send outgoing msgs.
TIMEOUT = 5 # How many seconds the control station will wait for a message before sending an error

class UDPRoverServer(QThread):
    onReceiveData = pyqtSignal('PyQt_PyObject')
    communicationTimeout = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        cfg.SETTINGSEVENT.addListener(self, self.onSettingsChanged)
        self.shouldDestroy = False
        self.messagesToSend = queue.Queue()    
        self.gamepadSocket = None
        self.sensorpubSocket = None
        self.lastSensorBroadcastAddress = None
        self.loadSettings(cfg.SETTINGS)
    
    def __del__(self):
        self.destroy()

    def connectToGamepadServer(self):
        self.gamepadSocket = QUdpSocket()
        self.gamepadSocket.bind(self.clientAddress, self.clientPort)

    def connectToSensorPublisher(self):        
        self.sensorpubSocket = QUdpSocket()
        self.sensorpubSocket.bind(QHostAddress.AnyIPv4, self.sensorBroadcastPort, QUdpSocket.ShareAddress)
        self.sensorpubSocket.joinMulticastGroup(self.sensorBroadcastAddress)
        self.lastSensorBroadcastAddress = self.sensorBroadcastAddress

    def disconnect(self):
        if self.gamepadSocket:
            self.gamepadSocket.close()

        if self.sensorpubSocket:
            if self.lastSensorBroadcastAddress:
                self.sensorpubSocket.leaveMulticastGroup(self.lastSensorBroadcastAddress)
            self.sensorpubSocket.close()

        self.gamepadSocket = None
        self.sensorpubSocket = None

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
        self.serverAddress = QHostAddress(config.get("communication", "serverGamepadAddress"))
        self.serverPort = int(config.get("communication", "serverGamepadPort"))      
        self.clientAddress = QHostAddress(config.get("communication", "clientGamepadAddress"))
        self.clientPort = int(config.get("communication", "clientGamepadPort"))     
        self.sensorBroadcastAddress = QHostAddress(config.get("communication", "serverRoverAddress"))
        self.sensorBroadcastPort = int(config.get("communication", "serverRoverPort"))    
        self.reconnect = True 

    def destroy(self):
        self.shouldDestroy = True
        self.wait()

    def run(self):
        lastMessageTime = time.time()
        while self.shouldDestroy == False:
            now = time.time()
            if self.reconnect:
                self.reconnect = False
                self.disconnect()
                self.connectToGamepadServer()
                self.connectToSensorPublisher()            
            
            # If the socket(s) are down, wait.
            if self.gamepadSocket is None or self.sensorpubSocket is None:
                time.sleep(TICK)   
                continue

            # I don't think the gamepad server on the rover will send replies, so this IF check can probably be removed!
            if self.gamepadSocket.hasPendingDatagrams():
                data, _, _ = self.gamepadSocket.readDatagram(self.gamepadSocket.pendingDatagramSize())
                if data is not None: # TODO Process incoming messages
                    lastMessageTime = now
                    print(data.decode())

            if self.sensorpubSocket.hasPendingDatagrams():
                data, _, _ = self.sensorpubSocket.readDatagram(self.sensorpubSocket.pendingDatagramSize())
                if data is not None:
                    print("Received Sensor Data:", data.decode())
                    lastMessageTime = now
                    obj = json.loads(data)
                    self.onReceiveData.emit(obj)
                    for _, v in obj.items(): # WIP!!! Could check incoming type here to decide what to do.
                        # handle message as value if type >= 0.
                        database.Event.add(v, 0, 0, str(datetime.datetime.now()))

            # Fetch messages from a thread-safe queue, if empty, skip and wait
            # for TICK time.
            d = self.fetchMessageToSend()
            if d:
                self.gamepadSocket.writeDatagram(d.encode(), self.serverAddress, self.serverPort)    

            # Check for inactivity, if no packet has been received within TIMEOUT sec, send signal to UI that we no longer have comms. with the rover.
            if (now - lastMessageTime) > TIMEOUT:
                self.communicationTimeout.emit(False)
                lastMessageTime = now
            elif now == lastMessageTime:
                self.communicationTimeout.emit(True)

            time.sleep(TICK)   

        self.disconnect()

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
    
