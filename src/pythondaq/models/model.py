from os import write
import csv
import numpy as np
from pythondaq.controllers.arduino_device import ArduinoVISADevice as AVD
from pythondaq.controllers.arduino_device import ConnectedDevs as CD
import os
import click
import pandas as pd

"""Module to model data obtained using the arduino_device module from the controllers.
"""


class ArduinoModel:
    def __init__(self, port="ASRL3::INSTR"):
        self.device = AVD(port=port)

    def deviceinfo(self):
        return self.device.get_id_string()

    def set_voltage(self, voltage):
        self.device.set_output_voltage(0, voltage)

    def meas_curr_diode(self):
        u_ch2 = float(self.device.get_input_voltage(2))
        return u_ch2 / 220

    def error(self, samplesize, nsteps):
        self.rawdatadf = pd.DataFrame()
        self.procddatadf = pd.DataFrame()
        for i in range(samplesize):
            for _ in self.sweep_waardes(nsteps, error=True):
                pass

            self.rawdatadf[f"{i}current"], self.rawdatadf[f"{i}voltage"] = (
                self.currentlist,
                self.voltagelist,
            )
        (
            self.procddatadf["mean current(A) "],
            self.procddatadf["mean voltage (V)"],
        ) = np.mean(
            self.rawdatadf.loc[:, ["current" in i for i in self.rawdatadf.columns]],
            axis=1,
        ), np.mean(
            self.rawdatadf.loc[:, ["voltage" in i for i in self.rawdatadf.columns]],
            axis=1,
        )
        self.procddatadf["error current"], self.procddatadf["error voltage"] = (
            np.std(
                self.rawdatadf.loc[:, ["current" in i for i in self.rawdatadf.columns]],
                axis=1,
            )
            / np.sqrt(samplesize),
            np.std(
                self.rawdatadf.loc[:, ["voltage" in i for i in self.rawdatadf.columns]],
                axis=1,
            )
            / np.sqrt(samplesize),
        )

        return self.procddatadf

    def sweep_waardes(self, nsteps, begin=0, eind=3.3):
        """Sweeps value settings and calculates amps and voltage.

        Sweeps value on output channel from 0 to 1024 and measures value over the LED component and the current through the resistor.
        Args:
            plot:
                set to True if you want to see a plot of the results, default is False
            print:
                set to True if you want a print of output value, voltage and measured value and voltage on channel 2, default is True"""
        voltagelist = []
        currentlist = []
        datalist = []
        stepsize = (eind - begin) / nsteps
        for n in np.arange(begin, eind, stepsize):

            self.device.set_output_voltage(0, n)

            u_ch0 = float(self.device.get_output_voltage(0))
            u_ch1 = float(self.device.get_input_voltage(1))
            val_ch2 = float(self.device.get_input_value(2))
            u_ch2 = float(self.device.get_input_voltage(2))
            I = u_ch2 / 220
            U = u_ch1 - u_ch2
            currentlist.append(I), voltagelist.append(U)
            datalist.append((I, U))
            if print == True:
                print(f"{n} {u_ch0:0.2f} Volt {val_ch2} {u_ch2:0.2f} Volt")

            yield I, U

        self.voltagelist = voltagelist
        self.currentlist = currentlist
        self.device.set_output_voltage(0, 0)
        self.datalist = datalist
        data = (self.voltagelist, self.currentlist)

        # return voltagelist, currentlist

    def reset_out(self):
        self.device.turn_off()

    def csv_maker(self, filename="data"):
        """Creates a csv file with the measurements and saves it under a unique name."""
        pad = os.getcwd()
        i = 0
        while os.path.exists(f"{pad+filename}{i}.csv"):
            i += 1

        with open(f"{pad+filename}{i}.csv", mode="w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(["Current (A)", "Voltage (V)"])
            for current, voltage in zip(self.currentlist, self.voltagelist):
                writer.writerow([current, voltage])


def listing(search):
    ports = CD()
    if search == "":
        print(f"The list of devices is:")
        for device in ports:
            print(f"{device}")

    else:
        found_devices = []
        for device in ports:
            if search in device:
                found_devices.append(device)

        if len(found_devices) == 0:
            print("No device was found matching the search phrase")
        else:
            print("The device(s) matching the search phrase are:")
            for item in found_devices:
                print(item)
