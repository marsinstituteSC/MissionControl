""" 
Initializes the rover UDP server. (currently acting as a dummy)
TODO: Implement ROS, listen to the 'right' nodes, bundle up a dictionary containing relevant data, send it to the multicast address. (test on the rover)
"""

import time
import json
import random
import signal

from PyQt5.QtNetwork import QUdpSocket, QHostAddress, QNetworkInterface

GAMEPAD_SERVER_ADDRESS = QHostAddress("127.0.0.1")
GAMEPAD_SERVER_PORT = 5000

SENSOR_PUBLISH_SERVER = QHostAddress("239.255.43.21")
SENSOR_PUBLISH_PORT = 45454

RUNNING = True

def generate_random_data():
    """
    Generates random sensor data, returns as a json object.
    """
    output = {}

    # Drive : Speed + Turn
    output["drive"] = {
        "speed": random.randint(0, 16),
        "turn": random.randint(-1, 1)
    }

    # Temperature
    output["temperature"] = random.randint(-30, 30)

    # Compass
    output["compass"] = random.randint(0, 360) 

    # Battery
    output["battery"] = {
        "voltage": random.randint(0, 12),
        "capacity": random.randint(0, 100) 
    }

    # Gyroscope
    output["rotation"] = {
        "roll": random.randint(0, 360),
        "pitch": random.randint(0, 360),
        "yaw": random.randint(0, 360)
    }

    # Status, TODO
    # output["status"] = <some string>

    # Message severity MAX 3 types
    output["severity"] = random.randint(0,3) # Common for all msgs.

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

    print("Starting server...")
    while RUNNING:
        if gamepadServer.hasPendingDatagrams():
            data, inAddress, inPort = gamepadServer.readDatagram(gamepadServer.pendingDatagramSize())
            print("IN :", data.decode())

        sensorPublisher.writeDatagram(generate_random_data(), SENSOR_PUBLISH_SERVER, SENSOR_PUBLISH_PORT)
        time.sleep(500 / 1000)

    # Cleanup
    gamepadServer.close()
    sensorPublisher.close()

    print("Stopped server...")