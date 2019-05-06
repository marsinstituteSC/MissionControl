from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
from widgets import logger as log

class TemperatureWidget(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("designer/widget_temperature.ui", self)
        self.temperature = None
        self.hide()

    def setTemperature(self, temp):
        try:
            self.temperature = float(temp)
        except:
            log.LOGGER_EVENTS.dispatchDirectLogEvent("TemperatureWidget received invalid temperature, '{}'.".format(temp), log.LOGGER_PRIORITY_WARNING)
            self.temperature = None
        
        if self.temperature:
            self.show()
            self.lcd_temperature.display(self.temperature)
        else:
            self.hide()