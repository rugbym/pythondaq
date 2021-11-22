import pyvisa as pv
import time
import matplotlib.pyplot as plt
from controllers.arduino_device import ArduinoVISADevice as AVD
from model.model import ArduinoModel as AM


device = AVD()
device.set_output_value(0, 700)
p = AM(device)
p.sweep_waardes(plot=True, print=False)
p.csv_maker()
device.turn_off()

device.set_output_voltage(0, 2.2)
device.get_output_voltage(0)
device.turn_off()
