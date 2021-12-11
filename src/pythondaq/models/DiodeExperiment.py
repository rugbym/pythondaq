# Parts of the code are copied or inspired from the module diode_experiment.py
# from the author David Fokkema. Placed on canvas as Uitwerkingen H6
import csv
import numpy as np
from statistics import mean, stdev
from pythondaq.controllers.arduino_device import ArduinoVISADevice as AVD
from pythondaq.controllers.arduino_device import ConnectedDevs as CD
import os
from math import sqrt
import threading

"""Module to model data obtained using the arduino_device module from the controllers.
"""


class DiodeExperiment:
    def __init__(self, port="ASRL3::INSTR"):
        """Initiates the class. Standard port is given to avoid typing or copy-pasting ports."""
        self.device = AVD(port=port)
        # Done so that the scan_data is always available
        self.scan_data = []
        self.U_list = []
        self.I_list = []
        self.U_err_list = []
        self.I_err_list = []

    def deviceinfo(self):
        """Info about the current connected device."""
        return self.device.get_id_string()

    def set_voltage(self, voltage):
        self.device.set_output_voltage(0, voltage)

    def meas_curr_diode(self):
        u_ch2 = float(self.device.get_input_voltage(2))
        return u_ch2 / 220

    def measure(self, samplesize=1):
        """Calculate current and voltage across diode using measurements.

        Args:
            N:
                The number of measurements to make. Integer value.
        Returns:
            A tuple consisting of the voltage, current and error on the voltage and current
            over the diode.
        """
        U, I = [], []
        for _ in range(samplesize):
            u_ch1 = float(self.device.get_input_voltage(1))
            u_ch2 = float(self.device.get_input_voltage(2))
            current = u_ch2 / 220
            diode_voltage = u_ch1 - u_ch2
            U.append(diode_voltage)
            I.append(current)
        if samplesize > 1:
            err_diode_voltage = stdev(U) / sqrt(samplesize)
            err_I = stdev(I) / sqrt(samplesize)
        else:
            err_diode_voltage = float("nan")
            err_I = float("nan")

        return mean(U), mean(I), err_diode_voltage, err_I

    def start_scan(self, nsteps, samplesize, begin, end):
        self._scan_thread = threading.Thread(
            target=self.scan, args=(nsteps, samplesize, begin, end)
        )
        self._scan_thread.start()

    def scan(self, nsteps, samplesize, begin=0, end=3.3):
        """Perform measurements across a range of voltages.

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
        self.scan_data = []
        self.U_list = []
        self.I_list = []
        self.U_err_list = []
        self.I_err_list = []
        for voltage in np.linspace(begin, end, nsteps):
            self.set_voltage(voltage)
            measurement = self.measure(samplesize)
            self.scan_data.append((voltage,) + measurement)
            u, i, u_err, i_err = measurement
            self.U_list.append(u)
            self.I_list.append(i)
            self.U_err_list.append(u_err)
            self.I_err_list.append(i_err)

        return self.scan_data

    def reset_out(self):
        """Sets the output of the device to 0"""
        self.device.turn_off()

    def csv_maker(self, filename, app=True):
        """Creates a csv file with the measurements and saves it under a unique name."""
        #
        if len(str.split(filename, ".csv")) == 1:
            filename = filename + ".csv"
        if app == True:
            pad = ""
        if app == False:
            pad = "\\Users\\mmael\\NSP2\\pythondaq\\pythondaq\\"

        i = 0
        name = str.split(filename, ".")
        while os.path.exists(f"{name[0]}{i}.{name[1]}"):
            i += 1

        with open(
            f"{name[0]}{i}.{name[1]}", mode="w", encoding="UTF8", newline=""
        ) as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(
                [
                    "Output voltage (V)",
                    "Mean current (A)",
                    "Mean voltage (V)",
                    "\u03B4 I (A)",
                    "\u03B4 U (V)",
                ]
            )
            for measurement in self.scan_data:
                writer.writerow(measurement)

    def close_session(self):
        self.device.disconnect_device()


def listing(search="", app=False):
    ports = CD()
    if app == False:
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
