""" Reading the input from a game controller """

import json

from pygame import joystick, time, event, init, quit, JOYBUTTONDOWN, JOYAXISMOTION, JOYHATMOTION, JOYBUTTONUP
from PyQt5.QtCore import QThread

from communications import udp_conn as UDP

# A lot of help from
# https://github.com/joncoop/pygame-xbox360controller/blob/master/xbox360_controller.py
# for class structure, methods and better deadzone calculations

GAMEPAD = None

ROVER_MAPPING_AXIS = {
    0 : 0,
    1 : 0,
    2 : 0,
    3 : 0,
    4 : 0,
    5 : 0,
    6 : 0,
    7 : 0
}

ROVER_MAPPING_BUTTONS = {
    0 : False,
    1 : False,
    2 : False,
    3 : False,
    4 : False,
    5 : False,
    6 : False,
    7 : False,
    8 : False,
    9 : False,
    10 : False
}

class Gamepad(QThread):
    """Class for gamepad"""
    # Init does not initialize the gamepad
    def __init__(self, deadzone=0.1):
        super().__init__()
        # Initializes pygame and creates a instance of a clock to control the
        # tick rate.
        init()
        self.CLOCK = time.Clock()
        self.shouldDestroy = False

        # Gamepad (pygame) mapping for Windows
        self.gamepad_mapping = {
            "A" : 0,
            "B" : 1,
            "X" : 2,
            "Y" : 3,
            "LB" : 4,
            "RB" : 5,
            "BACK" : 6,
            "START" : 7,
            "LEFT_STICK_BUTTON" : 8,
            "RIGHT_STICK_BUTTON" : 9,
            "LEFT_STICK_X" : 0,
            "LEFT_STICK_Y" : 1,
            "BUMPERS" : 2,
            "RIGHT_STICK_Y" : 3,
            "RIGHT_STICK_X" : 4
        }
        # Local instance of rover mapping
        self.rover_axis = ROVER_MAPPING_AXIS
        self.rover_buttons = ROVER_MAPPING_BUTTONS

        self.joystick = None
        self.deadzone = deadzone
        self.joystick_id = None
        joystick.init()
        self.initialize(0)

    def destroy(self):
        self.shouldDestroy = True

    # Initializes the joystick
    def initialize(self, id_joystick):
        """Initializes the selected joystick"""
        try:
            self.joystick_id = id_joystick
            self.joystick = joystick.Joystick(id_joystick)
            self.joystick.init()
        except:
            print("Invalid joystick num/ID,", id_joystick, "!")

    def get_all_gamepads(self):
        """
        Finds all connected joysticks
        Returns a dictionary with pygame id of joystick as key and name as value
        """
        joysticks = {}
        for i in range(joystick.get_count()):
            joysticks[i] = joystick.get_name()

        return joysticks

    def get_joystick_id(self):
        """
        Returns the joysticks id
        """
        return self.joystick_id

    def axis_value(self, value):
        """
        Deadzone calculations
        created by joncoop at github see link at the top
        """
        if value > self.deadzone:
            return (value - self.deadzone) / (1 - self.deadzone)
        elif value < -self.deadzone:
            return (value + self.deadzone) / (1 - self.deadzone)
        else:
            return 0

    def read_rover_buttons(self):
        """
        A lot like the get_buttons function, but specialized for the rover and does not return anything
        """
        self.rover_buttons[0] = bool(self.joystick.get_button(self.gamepad_mapping["A"]))
        self.rover_buttons[1] = bool(self.joystick.get_button(self.gamepad_mapping["B"]))
        self.rover_buttons[2] = bool(self.joystick.get_button(self.gamepad_mapping["Y"]))
        self.rover_buttons[3] = bool(self.joystick.get_button(self.gamepad_mapping["X"]))
        self.rover_buttons[4] = bool(self.joystick.get_button(self.gamepad_mapping["LB"]))
        self.rover_buttons[5] = bool(self.joystick.get_button(self.gamepad_mapping["RB"]))
        self.rover_buttons[6] = bool(self.joystick.get_button(self.gamepad_mapping["START"]))
        self.rover_buttons[7] = bool(self.joystick.get_button(self.gamepad_mapping["BACK"]))
        self.rover_buttons[8] = False # XBOX Button
        self.rover_buttons[9] = bool(self.joystick.get_button(self.gamepad_mapping["LEFT_STICK_BUTTON"]))
        self.rover_buttons[10] = bool(self.joystick.get_button(self.gamepad_mapping["RIGHT_STICK_BUTTON"]))

    def read_rover_axis(self):
        """
        Reads the axises and dpad values
        """
        # Left stick
        Lx = int(100 * self.axis_value(self.joystick.get_axis(self.gamepad_mapping["LEFT_STICK_X"])))
        Ly = int(-100 * self.axis_value(self.joystick.get_axis(self.gamepad_mapping["LEFT_STICK_Y"])))
        self.rover_axis[0] = Lx
        self.rover_axis[1] = Ly

        # Right stick
        Rx = int(100 * self.axis_value(self.joystick.get_axis(self.gamepad_mapping["RIGHT_STICK_X"])))
        Ry = int(-100 * self.axis_value(self.joystick.get_axis(self.gamepad_mapping["RIGHT_STICK_Y"])))
        self.rover_axis[3] = Rx
        self.rover_axis[4] = Ry

        # Bumpers NOTE Does not reset correctly
        value = int(100 * self.axis_value(self.joystick.get_axis(self.gamepad_mapping["BUMPERS"])))
        # Left bumper
        if value > 0:
            if value > 95:
                self.rover_axis[2] = 100
            else:
                self.rover_axis[2] = value
        # Right bumper
        elif value < 0:
            if value < -95:
                self.rover_axis[5] = -100
            else:
                self.rover_axis[5] = value

        elif value == 0:
            self.rover_axis[2] = 0
            self.rover_axis[5] = 0

        # D-pad
        Dx, Dy = self.joystick.get_hat(0)
        self.rover_axis[6] = Dx # X
        self.rover_axis[7] = -Dy # Y, need to flip it to correspond to the json specification

    # NOTE create a local variable to hold the gamepad value for the functions
    # we
    # will use.
    # Initializes pygame and creates a instance of a clock to control the tick
    # rate.
    def run(self):
        while self.shouldDestroy == False:
	        # Go through the event list and find button, axis and hat events
            for EVENT in event.get():
                eventHappened = False
                if EVENT.type == JOYBUTTONDOWN or EVENT.type == JOYBUTTONUP:
                    self.read_rover_buttons()
                    eventHappened = True

                if EVENT.type == JOYAXISMOTION or EVENT.type == JOYHATMOTION:
                    self.read_rover_axis()
                    eventHappened = True
                
                if eventHappened:
                    message = {
                        "Axis" : self.rover_axis,
                        "Buttons" : self.rover_buttons
                    }
                    print(message)
                    UDP.ROVERSERVER.writeToRover(json.dumps(message, separators=(',', ':')))

            # Limit the clock rate to 30 ticks per second
            self.CLOCK.tick(30)

        quit()

def loadGamepad():
    global GAMEPAD
    GAMEPAD = Gamepad()
    GAMEPAD.start()
    return GAMEPAD

def shutdownGamepad():
    global GAMEPAD
    if GAMEPAD is None:
        return

    GAMEPAD.destroy()
    GAMEPAD = None