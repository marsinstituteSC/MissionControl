""" Starts a test server which can act as the Rover UDP server. """

import PyQt5.QtCore
import PyQt5.QtNetwork

import time, json, random
def generate_random_data():
    """
    Generates random sensor data and returns a json object
    Data:
        Speed: 0-5 m/s
        Temperature: -60 to 20 degrees Celsius
        ...
    """
    output = {}
    # Speed generation
    output["speed"] = random.randint(0, 6)

    # Temperature generation
    output["temperature"] = random.randint(-60, 21)

    return json.dumps(output)


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

