from os import write
from time import struct_time
import matplotlib.pyplot as plt
import datetime
import csv
import os


class ArduinoModel:
    def __init__(self, device):
        self.device = device

    def sweep_waardes(self, plot=False, print=True):
        """Sweeps value settings and calculates amps and voltage.

        Sweeps value on output channel from 0 to 1024 and measures value over the LED component and the current through the resistor.
        Args:
            plot:
                set to True if you want to see a plot of the results, default is False
            print:
                set to True if you want a print of output value, voltage and measured value and voltage on channel 2, default is True"""
        self.voltagelist = []
        self.currentlist = []
        for n in range(0, 1024):

            self.device.set_output_value(0, n)

            u_ch0 = float(self.device.get_output_voltage(0))
            u_ch1 = float(self.device.get_input_voltage(1))
            val_ch2 = float(self.device.get_input_value(2))
            u_ch2 = float(self.device.get_input_voltage(2))
            I = u_ch2 / 220
            V = u_ch1 - u_ch2
            self.currentlist.append(I), self.voltagelist.append(V)

            if print == True:
                print(f"{n} {u_ch0:0.2f} Volt {val_ch2} {u_ch2:0.2f} Volt")

        self.device.set_output_voltage(0, 0)
        if plot == True:
            self.plot()

    def plot(self):
        """Plots the voltage vs the current"""
        plt.plot(self.voltagelist, self.currentlist)
        plt.xlabel("Voltage over LED (V)"), plt.ylabel("Current over LED (A)")
        plt.show()

    def csv_maker(self):
        """Creates a csv file with the measurements and saves it under unique name."""
        currenttime = str(datetime.datetime.today())
        timestring = str.split(currenttime, sep=".")[0]
        name = "bestand" + timestring + ".csv"
        path = os.getcwd() + "\\"

        newfile = "water.csv"
        with open(newfile, mode="w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(["Current (A)", "Voltage (V)"])
            for current, voltage in zip(self.currentlist, self.voltagelist):
                writer.writerow([current, voltage])
