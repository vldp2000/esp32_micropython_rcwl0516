import machine
from machine import Pin

__version__ = '0.1.0'
__author__ = 'Vlad Perepelytsya'
__license__ = "Apache License 2.0. https://www.apache.org/licenses/LICENSE-2.0"

class RCWL0516:
    """
    Driver to use the sensor RCWL-0516.
    """
    def __init__(self, triggerPin, lightSensorPin):
        """
        trigger_pin: Output pin to send pulses
        lightSensorPin: 
        """
        # Init trigger pin (in)
        self.trigger = Pin(triggerPin , mode=Pin.IN, pull=None)

        # Init echo pin (out)
        self.lightSensor = Pin(lightSensorPin, mode=Pin.OUT, pull=None)
        self.lightSensor.value(1)

    def readMotion(self):
        return self.trigger()
