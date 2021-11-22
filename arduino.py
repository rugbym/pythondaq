import pyvisa as pv
import time
import matplotlib.pyplot as plt
from controllers.arduino_device import ArduinoVISADevice


device = ArduinoVISADevice()
device.set_output_value(0, 700)
device.sweep_waardes(True, print=False)
device.turn_off()
device.set_output_voltage(0, 2.2)
device.get_output_voltage(0)
device.get_input_voltage(2)
