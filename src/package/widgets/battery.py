from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi
import sys


class BatteryWidget(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("designer/widget_battery.ui", self)

        # Contain all status images of battery in dictionary for ease of use.
        self.batteryStatus = {
            "full": QPixmap("images/status icons/battery_full.png"),
            "threequarter": QPixmap("images/status icons/battery_quarter.png"),
            "half": QPixmap("images/status icons/battery_half.png"),
            "onequarter": QPixmap("images/status icons/battery_almostEmpty.png"),
            "empty": QPixmap("images/status icons/battery_empty.png")
        }

        # Battery state is to prevent redrawing the image if there has been no change
        self.batteryState = "full"

        self.voltage = "0"
        self.capacity = "0"
        self.label_voltage.setText(self.voltage + "V")
        self.label_capacity.setText(self.capacity + "%")
        self.label_battery.setPixmap(self.batteryStatus["empty"])

    def setVoltage(self, voltage):
        try:
            self.voltage = str(voltage)
            self.label_voltage.setText(self.voltage + "V")
        except:
            print("Voltage Error")

    def setCapacity(self, capacity):
        try:
            capacity = int(capacity)
            self.capacity = str(capacity)
            self.label_capacity.setText(self.capacity + "%")
        except:
            print("Capacity Error")

        img = "empty"
        if capacity > 75:
            img = "full"
        elif capacity > 50:
            img = "threequarter"
        elif capacity > 25:
            img = "half"
        elif capacity > 0:
            img = "onequarter"

        if img not in self.batteryState:
            self.label_battery.setPixmap(self.batteryStatus[img])
            self.batteryState = img

    def getVoltage(self):
        return self.voltage

    def getCapacity(self):
        return self.capacity
