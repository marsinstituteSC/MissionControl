""" Starts a test server which can act as the Rover UDP server. """

import time
import json
import random
import signal
import sys

from PyQt5.QtNetwork import QUdpSocket, QHostAddress, QNetworkInterface

GAMEPAD_SERVER_ADDRESS = QHostAddress("127.0.0.1")
GAMEPAD_SERVER_PORT = 5000

SENSOR_PUBLISH_SERVER = QHostAddress("239.255.43.21")
SENSOR_PUBLISH_PORT = 45454

RUNNING = True


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

    return json.dumps(output).encode()


def startGamepadListener():
    s = QUdpSocket()
    s.bind(GAMEPAD_SERVER_ADDRESS, GAMEPAD_SERVER_PORT)
    return s


def startSensorMulticastPublisher():
    s = QUdpSocket()
    s.bind(QHostAddress.AnyIPv4, 0)
    return s


def shutdown(sig, frame):
    global RUNNING
    RUNNING = False


if __name__ == "__main__":
    # Receive gamepad changes from client (control station)
    gamepadServer = startGamepadListener()
    # Start a multicast publisher which writes to the given mcast addr. so that we can read a 'stream' of sensor changes, multiple clients can read from this stream too!
    sensorPublisher = startSensorMulticastPublisher()

    signal.signal(signal.SIGINT, shutdown)

    b = "Yes, I'm here!".encode()
    while RUNNING:
        print("waiting...")

        if gamepadServer.hasPendingDatagrams():
            data, inAddress, inPort = gamepadServer.readDatagram(
                gamepadServer.pendingDatagramSize())
            print("Recv:", data.decode())
            gamepadServer.writeDatagram(b, inAddress, inPort)

        print("Sending on multicast!")
        sensorPublisher.writeDatagram(
            generate_random_data(), SENSOR_PUBLISH_SERVER, SENSOR_PUBLISH_PORT)

        time.sleep(200 / 1000)

    # Cleanup
    gamepadServer.close()
    sensorPublisher.close()

    print("Closed server...")
