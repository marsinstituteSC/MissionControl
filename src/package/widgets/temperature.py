from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

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
            print("Temperature Error")
        
        if self.temperature:
            self.show()
            self.lcd_temperature.display(self.temperature)
        else:
            self.hide()