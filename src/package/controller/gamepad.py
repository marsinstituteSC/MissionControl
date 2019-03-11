""" Reading the input from a game controller """

import json, time

from pygame import joystick, time as pygameTime, event, init, quit, JOYBUTTONDOWN, JOYAXISMOTION, JOYHATMOTION, JOYBUTTONUP
from PyQt5.QtCore import QThread, pyqtSignal

from communications import udp_conn as UDP
from utils.math import clamp

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

GAMEPAD_TIMEOUT_TICK_TIME = (30 * 10) # 30 TICKS = 1 SEC, 30 * 30 = 30 SEC. Check gamepad status every 30 sec.
GAMEPAD_TIMEOUT = 10

class Gamepad(QThread):
    """Class for gamepad"""
    statusChanged = pyqtSignal(bool)
    refreshedGamepad = pyqtSignal(dict)

    # Init does not initialize the gamepad
    def __init__(self, deadzone=0.1):
        super().__init__()
        # Initializes pygame and creates a instance of a clock to control the
        # tick rate.
        init()

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

        self.needRefresh = False
        self.joystick = None
        self.joystick_id = -1
        self.joystick_id_switch = -1
        self.deadzone = deadzone        

    def destroy(self):
        self.shouldDestroy = True

    # Initializes the joystick
    def initialize(self, id_joystick):
        """Initializes the selected joystick"""
        try:
            if self.joystick:
                self.joystick.quit()

            self.joystick_id = id_joystick
            self.joystick = joystick.Joystick(id_joystick)
            self.joystick.init()
        except:
            self.joystick_id = -1
            print("Invalid joystick num/ID,", id_joystick, "!")

    def get_all_gamepads(self):
        """
        Finds all connected joysticks
        Returns a dictionary with pygame id of joystick as key and name as value
        """
        joysticks = {}
        for i in range(joystick.get_count()):
            stick = joystick.Joystick(i)
            stick.init()
            joysticks[i] = stick.get_name()
            stick.quit()

        return joysticks
    
    def refresh(self):
        """
        Finds all connected gamepads. Must be called at the start of the run loop if there has been a change.
        Will uninitialize and then initialize the joystick module
        """
        if self.joystick:
            self.joystick.quit()
            self.joystick = None

        joystick.quit()
        joystick.init()
        joyDictList = self.get_all_gamepads() # Must be fetched before initializing the ID, since otherwise we delete that ID afterwards, apparently the objects here are global!
        if joystick.get_count() > 1:
            self.initialize(clamp(self.joystick_id, 0, joystick.get_count()))
        elif joystick.get_count() == 1:
            self.initialize(0)
        self.refreshedGamepad.emit(joyDictList)
        self.statusChanged.emit(self.joystick.get_init() if self.joystick else False)

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
            newValue = (value - self.deadzone) / (1 - self.deadzone)
            if newValue > 0.95:
                return 1
            else:
                return newValue
        elif value < -self.deadzone:
            newValue = (value + self.deadzone) / (1 - self.deadzone)
            if newValue < -0.95:
                return -1
            else:
                return newValue
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
        Returns a boolean to identify if there has been a change.
        """
        changed = False
        # Left stick
        Lx = int(100 * self.axis_value(self.joystick.get_axis(self.gamepad_mapping["LEFT_STICK_X"])))
        Ly = int(-100 * self.axis_value(self.joystick.get_axis(self.gamepad_mapping["LEFT_STICK_Y"])))
        if Lx != self.rover_axis[0]:
            self.rover_axis[0] = Lx
            changed = True
        if Ly != self.rover_axis[1]:
            self.rover_axis[1] = Ly
            changed = True

        # Right stick
        Rx = int(100 * self.axis_value(self.joystick.get_axis(self.gamepad_mapping["RIGHT_STICK_X"])))
        Ry = int(-100 * self.axis_value(self.joystick.get_axis(self.gamepad_mapping["RIGHT_STICK_Y"])))
        if Rx != self.rover_axis[3]:
            self.rover_axis[3] = Rx
            changed = True
        if Ry != self.rover_axis[4]:
            self.rover_axis[4] = Ry
            changed = True

        # Bumpers NOTE Does not reset correctly
        # Multiply with 255 for JSON specification
        value = int(255 * self.axis_value(self.joystick.get_axis(self.gamepad_mapping["BUMPERS"])))
        # Left bumper
        if value > 0:
            self.rover_axis[2] = value
            changed = True
        # Right bumper
        elif value < 0:
            self.rover_axis[5] = value
            changed = True

        elif value == 0:
            self.rover_axis[2] = 0
            self.rover_axis[5] = 0
            changed = True

        # D-pad
        Dx, Dy = self.joystick.get_hat(0)
        if Dx != self.rover_axis[6]:
            self.rover_axis[6] = Dx # X
            changed = True
        if -Dy != self.rover_axis[7]:
            self.rover_axis[7] = -Dy # Y, need to flip it to correspond to the json specification
            changed = True
        return changed

    # NOTE create a local variable to hold the gamepad value for the functions
    # we
    # will use.
    # Initializes pygame and creates a instance of a clock to control the tick
    # rate.
    def run(self):
        CLOCK = pygameTime.Clock()
        self.refresh() # Startup Gamepad.
        lastEventTime = time.time()
 
        while self.shouldDestroy == False:
            now = time.time()
            if self.needRefresh: # User wants to check for newly connected or disconnected gamepad, reinits list + gamepads stuff.
                self.refresh()
                self.needRefresh = False
                lastEventTime = now
                continue

            if self.joystick_id_switch >= 0: # User wants to select a different gamepad!
                self.initialize(self.joystick_id_switch)
                self.joystick_id_switch = -1
                continue
                
            # Go through the event list and find button, axis and hat events
            for EVENT in event.get():
                eventHappened = False
                if EVENT.type == JOYBUTTONDOWN or EVENT.type == JOYBUTTONUP:
                    self.read_rover_buttons()
                    eventHappened = True

                if EVENT.type == JOYAXISMOTION or EVENT.type == JOYHATMOTION:
                    if self.read_rover_axis():
                        eventHappened = True
                
                if eventHappened:
                    lastEventTime = now
                    message = {
                        "Axis" : self.rover_axis,
                        "Buttons" : self.rover_buttons
                    }
                    print(message)
                    UDP.ROVERSERVER.writeToRover(json.dumps(message, separators=(',', ':')))
            
            if now - lastEventTime >= GAMEPAD_TIMEOUT:
                self.refresh()
                lastEventTime = now
            # Force refresh when no gamepad is connected for quicker reconnect. It's a elif in order to not get double refresh's.
            elif joystick.get_count() == 0:
                self.refresh()

            # Limit the clock rate to 30 ticks per second
            CLOCK.tick(30)

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
