""" Starts a test server which can act as the Rover UDP server. """

import PyQt5.QtCore
import PyQt5.QtNetwork

import time

if __name__ == "__main__":
    s = PyQt5.QtNetwork.QUdpSocket()
    addr = PyQt5.QtNetwork.QHostAddress("127.0.0.1")
    port = 5000
    s.bind(addr, port)
    b = "Yes, I'm here!".encode()
    while True:
        print("waiting...")
        if s.hasPendingDatagrams():
            data, inAddress, inPort = s.readDatagram(s.pendingDatagramSize())
            print("Recv:", data.decode())
            s.writeDatagram(b, inAddress, inPort)
        time.sleep(200 / 1000)
