"""
Simple event handler class, listeners should inherit EventListener.
"""


class EventListener():
    def onEvent(self, e):
        pass


class Event():
    def __init__(self, name=None):
        self.name = name
        self.listeners = list()

    def addListener(self, obj):
        if obj in self.listeners:
            print("{} is already listening to this event!".format(str(obj)))
            return

        if not issubclass(type(obj), EventListener):
            print("Listener has to implement EventListener!")
            return

        self.listeners.append(obj)

    def removeListener(self, obj):
        if obj in self.listeners:
            self.listeners.remove(obj)
        else:
            print("{} is not listening to this event!".format(str(obj)))

    def raiseEvent(self):
        for listener in self.listeners:
            listener.onEvent(self.name)

    def __repr__(self):
        return self.name
