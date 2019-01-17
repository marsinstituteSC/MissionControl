""" Reading the input from a game controller """

from pygame import joystick, time, event, init, JOYBUTTONDOWN, JOYAXISMOTION, JOYHATMOTION, JOYBUTTONUP
from PyQt5.QtCore import QThread

from utils import warning
import json

# A lot of help from
# https://github.com/joncoop/pygame-xbox360controller/blob/master/xbox360_controller.py
# for class structure, methods and better deadzone calculations

ROVER_MAPPING_BUTTONS = {
    "A": 0,
    "B": 1,
    "Y": 2,
    "X": 3,
    "LB": 4,
    "RB": 5,
    "START": 6
}

ROVER_MAPPING_AXIS = {
    "LEFT_STICK_X": 0,
    "LEFT_STICK_Y": 1,
    "BUMPERS_LEFT": 2,  # TODO, Names for left and right bumper?!
    "RIGHT_STICK_X": 3,
    "RIGHT_STICK_Y": 4,
    "BUMPERS_RIGHT": 5,  # TODO, Names for left and right bumper?!
    "ARROW_X": 6,  # TODO, name?
    "ARROW_Y": 7  # TODO, name?
}

def getKeyAsJsonFormattedString(typ, key, value):
    """
    Use the mapping documented for the rover to create a json object (string) 
    which can be sent to the rover.
    """
    # TODO, are values within range?
    if typ == "Axis":
        return json.dumps({"Axis": {ROVER_MAPPING_AXIS.get(key): value}}, separators=(',', ':'))
    else:
        return json.dumps({"Buttons": {ROVER_MAPPING_BUTTONS.get(key): value}}, separators=(',', ':'))

class Gamepad(QThread):
    """Class for gamepad"""
    # Init does not initialize the gamepad
    def __init__(self, deadzone=0.1):
        QThread.__init__(self)

        # Initializes pygame and creates a instance of a clock to control the
        # tick rate.
        init()
        self.CLOCK = time.Clock()

        # Gamepad mapping for Windows
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
        self.joystick = None
        self.deadzone = deadzone
        self.joystick_id = None
        joystick.init()
        self.initialize(0)

    def __del__(self):
        self.wait()    

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

    def get_buttons(self):
        """
        Reads the values from the buttons
        Returns a dictionary with button name as key and button state as value
        """
        button_states = {
            "A" : self.joystick.get_button(self.gamepad_mapping["A"]),
            "B" : self.joystick.get_button(self.gamepad_mapping["B"]),
            "X" : self.joystick.get_button(self.gamepad_mapping["X"]),
            "Y" : self.joystick.get_button(self.gamepad_mapping["Y"]),
            "LB" : self.joystick.get_button(self.gamepad_mapping["LB"]),
            "RB" : self.joystick.get_button(self.gamepad_mapping["RB"]),
            "BACK" : self.joystick.get_button(self.gamepad_mapping["BACK"]),
            "START" : self.joystick.get_button(self.gamepad_mapping["START"]),
            "LEFT_STICK_BUTTON" : self.joystick.get_button(self.gamepad_mapping["LEFT_STICK_BUTTON"]),
            "RIGHT_STICK_BUTTON" : self.joystick.get_button(self.gamepad_mapping["RIGHT_STICK_BUTTON"])
        }

        return button_states

    def get_left_stick(self):
        """
        Returns a x and y tuple
        Negative values are left and up
        Positive values are right and down
        """
        x = self.axis_value(self.joystick.get_axis(self.gamepad_mapping["LEFT_STICK_X"]))
        y = self.axis_value(self.joystick.get_axis(self.gamepad_mapping["LEFT_STICK_Y"]))

        return (x, y)

    def get_right_stick(self):
        """
        Returns a x and y tuple
        Negative values are left and up
        Positive values are right and down
        """
        x = self.axis_value(self.joystick.get_axis(self.gamepad_mapping["RIGHT_STICK_X"]))
        y = self.axis_value(self.joystick.get_axis(self.gamepad_mapping["RIGHT_STICK_Y"])) 

        return (x, y)

    def get_bumpers(self):
        """
        Returns the value from the bumpers
        Will use the deadzone
        Negative is RB and Positive means LB
        """
        value = self.axis_value(self.joystick.get_axis(self.gamepad_mapping["BUMPERS"]))
        if value > 0.99:
            return 1
        elif value < -0.99:
            return -1
        return value

    def get_dpad(self):
        """
        Returns a tuple (left, up, right, down) from the d-pad
        """
        x, y = self.joystick.get_hat(0)
        up = int(y == 1)
        down = int(y == -1)
        left = int(x == -1)
        right = int(x == 1)

        return (left, up, right, down)

    # NOTE create a local variable to hold the gamepad value for the functions
    # we
    # will use.
    # Initializes pygame and creates a instance of a clock to control the tick
    # rate.
    def run(self):
        while True:
	        # Go through the event list and find button, axis and hat events
            for EVENT in event.get():
		        # If a press event has happened, check the corresponding button and
		        # check if it is already pressed in before this event.
		        # TODO: Call the corresponding method for the key.
                if EVENT.type == JOYBUTTONDOWN or EVENT.type == JOYBUTTONUP:
                    for btn, value in self.get_buttons().items():
                        print(btn, value)

                if EVENT.type == JOYAXISMOTION:
                    print(self.get_left_stick())
                    print(self.get_right_stick())
                    print(self.get_bumpers())

                if EVENT.type == JOYHATMOTION:
                    print(self.get_dpad())

            # Limit the clock rate to 30 ticks per second
            self.CLOCK.tick(30)

def loadGamepad():
    pad = Gamepad()
    pad.start()
    return pad
