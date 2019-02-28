from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi
import sys

class BatteryWidget(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("designer/widget_battery.ui", self)

        self.batteryStatus = {
            "full" : QPixmap("images/status icons/battery_full.png"),
            "threequarter" : QPixmap("images/status icons/battery_quarter.png"),
            "half" : QPixmap("images/status icons/battery_half.png"),
            "onequarter" : QPixmap("images/status icons/battery_almostEmpty.png"),
            "empty" : QPixmap("images/status icons/battery_empty.png")
        }
        
        # Battery state is to prevent redrawing the image if there has been no change
        # 4 = Full, 3 = Three Quarter, 2 = Half, 1 = One Quarter, 0 = Empty
        self.batteryState = 4

        self.voltage = "0"
        self.capacity = "100"
        self.label_voltage.setText(self.voltage + "V")
        self.label_capacity.setText(self.capacity + "%")
        self.label_battery.setPixmap(self.batteryStatus["full"])

    def setVoltage(self, voltage):
        self.voltage = str(voltage)
        self.label_voltage.setText(self.voltage + "V")

    def setCapacity(self, capacity):
        capacity = int(capacity)
        self.capacity = str(capacity)
        self.label_capacity.setText(self.capacity + "%")
        if capacity == 0 and self.batteryState != 0:
            self.label_battery.setPixmap(self.batteryStatus["empty"])
            self.batteryState = 0
        elif capacity > 0 and capacity <= 25 and self.batteryState != 1:
            self.label_battery.setPixmap(self.batteryStatus["onequarter"])
            self.batteryState = 1
        elif capacity > 25 and capacity <= 50 and self.batteryState != 2:
            self.label_battery.setPixmap(self.batteryStatus["half"])
            self.batteryState = 2
        elif capacity > 50 and capacity <= 75 and self.batteryState != 3:
            self.label_battery.setPixmap(self.batteryStatus["threequarter"])
            self.batteryState = 3
        elif capacity > 75 and capacity <= 100 and self.batteryState != 4:
            self.label_battery.setPixmap(self.batteryStatus["full"])
            self.batteryState = 4
    
    def getVoltage(self):
        return self.voltage
    def getCapacity(self):
        return self.capacity
