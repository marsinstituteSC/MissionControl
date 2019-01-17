""" Establishes a UDP connection with the Rover, implements methods for sending & receiving data! """

import PyQt5.QtCore
import PyQt5.QtNetwork
import time
import queue

SERVERHOST = '127.0.0.1' # 192.168.1.3
SERVERPORT = 5000

CLIENTHOST = '127.0.0.1'
CLIENTPORT = 37500

ROVERSERVER = None # Allow other files/pgks to easily access our udp server through this global.
TICK = (50 / 1000) # How often in msec should we check inc / send outgoing msgs.
class UDPRoverServer(PyQt5.QtCore.QThread):
    def __init__(self):
        super().__init__()
        self.messagesToSend = queue.Queue()
        self.connect()

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
        while True:
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