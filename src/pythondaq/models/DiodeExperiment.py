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


class DiodeExperiment:
    def __init__(self, port="ASRL3::INSTR"):
        """Initiates the class. Standard port is given to avoid typing or copy-pasting ports."""
        self.device = AVD(port=port)

    def deviceinfo(self):
        """Info about the current connected device."""
        return self.device.get_id_string()

    def set_voltage(self, voltage):
        self.device.set_output_voltage(0, voltage)

    def meas_curr_diode(self):
        u_ch2 = float(self.device.get_input_voltage(2))
        return u_ch2 / 220

    def error(self, samplesize, nsteps, begin, end):
        """Calculates the error on current and voltage over the diode
        based on given number of measurements.

        Generates a measurement and then uses
        the list stored in the class to add to its frame of measurements. Calculates
        the mean and the error over the values.

        Args:
            samplesize:
                The number of measurements to make
            nsteps:
                The number of steps to take between the begin and end voltage
            begin:
                Starting voltage value of the sweep
            end:
                Ending value of the sweep
        """
        self.rawdatadf = pd.DataFrame()
        self.procddatadf = pd.DataFrame()
        for i in range(samplesize):
            for _ in self.sweep_values(nsteps, begin=begin, end=end):
                pass

            self.rawdatadf[f"{i}current"], self.rawdatadf[f"{i}voltage"] = (
                self.currentlist,
                self.voltagelist,
            )
        (
            self.procddatadf["mean current (A)"],
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

    def sweep_values(self, nsteps, begin=0, end=3.3):
        """Sweeps value settings and calculates amps and voltage.

        Sweeps value on output channel from 0 to 3.3V and measures voltage over the LED component and the current through the resistor.
        yields the current and voltage and creates a list stored in the class.
        Args:
            nsteps:
                number of steps to take between the beginning of the measurement and the end. Stepsize is calculated accordingly.
            begin:
                Starting of the voltage sweep. Voltage 0<=begin<=3.3.
            end:
                Ending of the voltage sweep. Voltage 0<=begin<=3.3."""
        voltagelist = []
        currentlist = []
        datalist = []
        stepsize = (end - begin) / nsteps
        for n in np.arange(begin, end, stepsize):

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
        """Sets the output of the device to 0"""
        self.device.turn_off()

    def csv_maker(self, error, filename="data", app=True):
        """Creates a csv file with the measurements and saves it under a unique name."""
        #
        if app == True:
            pad = ""
        if app == False:
            pad = "\\Users\\mmael\\NSP2\\pythondaq\\pythondaq\\"
        i = 0
        name = str.split(filename, ".")
        while os.path.exists(f"{name[0]}{i}.{name[1]}"):
            i += 1

        if error == False:
            with open(
                f"{name[0]}{i}.{name[1]}", mode="w", encoding="UTF8", newline=""
            ) as f:
                writer = csv.writer(f, delimiter=",")
                writer.writerow(["Current (A)", "Voltage (V)"])
                for current, voltage in zip(self.currentlist, self.voltagelist):
                    writer.writerow([current, voltage])
        else:
            with open(
                f"{name[0]}{i}.{name[1]}", mode="w", encoding="UTF8", newline=""
            ) as f:
                writer = csv.writer(f, delimiter=",")
                writer.writerow(
                    [
                        "Mean current (A)",
                        "Mean voltage (V)",
                        "\u03B4 I (A)",
                        "\u03B4 U (V)",
                    ]
                )
                for current, voltage, errorcurrent, errorvoltage in zip(
                    self.procddatadf["mean current (A)"],
                    self.procddatadf["mean voltage (V)"],
                    self.procddatadf["error current"],
                    self.procddatadf["error voltage"],
                ):
                    writer.writerow([current, voltage, errorcurrent, errorvoltage])
    
    def close_session(self):
        self.device.disconnect_device()

def listing(search='',app=False):
    ports = CD()
    if app==False:    
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
    
    return ports
