"""
Simple event handler class. Events can be defined globally and can be raised by any func, class, etc...
When raised, the event will notify all listeners via calling their given function arguments.
"""

class Event():
    def __init__(self, name=None):
        self.name = name
        self.listeners = dict()

    def __repr__(self):
        if self.name is not None:
            return self.name
        else:
            return "Event()"

    def __del__(self):
        self.clearListeners()

    def addListener(self, obj, func):
        self.listeners[obj] = func

    def removeListener(self, obj):
        try:
            self.listeners.pop(obj)
        except:
            print("{} is not listening to this event!".format(str(obj)))

    def clearListeners(self):
        self.listeners.clear()

    def raiseEvent(self, params=None):
        for _, v in self.listeners.items():
            v(self.name, params)
