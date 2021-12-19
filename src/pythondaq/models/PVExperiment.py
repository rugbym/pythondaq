from os import write
import csv
import numpy as np
from scipy.constants import Boltzmann, elementary_charge
from scipy.stats import linregress
from statistics import mean, stdev
from math import sqrt
import threading
from pythondaq.controllers.arduino_device import ArduinoVISADevice as AVD
from pythondaq.controllers.arduino_device import ConnectedDevs as CD
import os
import pandas as pd
import lmfit
from lmfit import models

"""Module to model data obtained using the arduino_device module from the controllers.
"""
# Moet nog toepassen: veranderingen aan hoofdstuk 7, stroom van de zonnepaneel is stroom van de
# weerstanden bij elkaar opgeteld, P = V I


class PVExperiment:
    def __init__(self, port="ASRL3::INSTR"):
        """Initiates the class. Standard port is given to avoid typing or copy-pasting ports."""
        self.device = AVD(port=port)
        self._scan_thread = None
        self.get_max_point = False
        self.scan_data = []
        self.U_list = []
        self.I_list = []
        self.P_list = []
        self.U_err_list = []
        self.I_err_list = []
        self.P_err_list = []
        self.U_zero_list = []
        self.R_MOSFET_list = []
        self.R_MOSFET_err_list = []
        self.fit_plot_list = []
        self.x = []
        self.slope = []
        self.slope_height = []
        self.startvalue = 0
        self.stopvalue = 3.3

    def deviceinfo(self):
        """Info about the current connected device."""
        return self.device.get_id_string()

    def set_voltage(self, voltage):
        self.device.set_output_voltage(0, voltage)

    def meas_curr_diode(self):
        u_ch2 = float(self.device.get_input_voltage(2))
        return u_ch2 / 220

    def u_pv_u_zero(self):
        """First draft for calculating voltages"""
        nsteps, begin, end = 1000, 0, 3.3
        stepsize = (end - begin) / nsteps

        u_zerolist = []
        u_pvlist = []
        datalist = []
        for n in np.arange(begin, end, stepsize):

            self.device.set_output_voltage(0, n)

            u_ch0 = float(self.device.get_output_voltage(0))
            u_ch1 = float(self.device.get_input_voltage(1))

            u_pv = 3 * u_ch1
            u_zerolist.append(u_ch0), u_pvlist.append(u_pv)
            datalist.append((u_ch0, u_pv))

        self.u_zerolist = u_zerolist
        self.u_pvlist = u_pvlist

    def measure(self, samplesize=1):
        """Calculate current and voltage across diode using measurements.

        Args:
            N:
                The number of measurements to make. Integer value.
        Returns:
            A tuple consisting of the voltage, current and error on the voltage and current
            over the diode.
        """
        U, I, P, R = [], [], [], []
        for _ in range(samplesize):
            u_ch1 = float(self.device.get_input_voltage(1))
            u_ch2 = float(self.device.get_input_voltage(2))
            I_mosfet = u_ch2 / 4.7
            I_ch1 = u_ch1 / (10 ** 6)
            I_pv = I_mosfet + I_ch1

            u_pv = 3 * u_ch1
            p_pv = u_pv * I_pv
            try:
                R_mosfet = (u_pv - u_ch2) / I_mosfet
            except ZeroDivisionError:
                R_mosfet = (u_pv - u_ch2) / 0.000001

            U.append(u_pv)
            I.append(I_pv)
            P.append(p_pv)
            R.append(R_mosfet)

        if samplesize > 1:
            err_pv_voltage = stdev(U) / sqrt(samplesize)
            err_pv_I = stdev(I) / sqrt(samplesize)
            err_pv_power = stdev(P) / sqrt(samplesize)
            try:
                err_mosfet_R = stdev(R) / sqrt(samplesize)
            except stdev(R) / sqrt(samplesize) == 0:
                err_mosfet_R = 0.00001
        else:
            err_pv_voltage = float("nan")
            err_pv_I = float("nan")
            err_pv_power = float("nan")
            err_mosfet_R = float("nan")

        return (
            mean(U),
            mean(I),
            mean(P),
            mean(R),
            err_pv_voltage,
            err_pv_I,
            err_pv_power,
            err_mosfet_R,
        )

    def start_scan(self, nsteps, samplesize, begin, end, startvalues=False):
        """Allows for threading and simultanious execution of code
        Starts the thread in this function"""
        self._scan_thread = threading.Thread(
            target=self.scan, args=(nsteps, samplesize, begin, end, startvalues)
        )
        self._scan_thread.start()

    def fit_it(self):
        """Fits the U,I-data to a model.

        Uses average of last 2 points of the current to set starting parameter
        for I_l.
        """
        self.fit_plot_list = []
        fitfunc = lambda U, n, T, I_l, I_0, e, k: I_l - I_0 * (
            np.exp((e * U) / (n * T * k)) - 1
        )
        model = models.Model(fitfunc)
        params = model.make_params()
        params.add("T", value=293, vary=False)
        params.add("n", value=17)
        params.add("e", value=elementary_charge, vary=False)
        params.add("k", value=Boltzmann, vary=False)
        params.add("I_l", value=mean(self.I_list[-2:]))
        params.add("I_0", value=0.0)

        self.fit = model.fit(
            U=np.array(self.U_list),
            data=np.array(self.I_list),
            weights=1 / np.array(self.I_err_list),
            params=params,
        )

        self.n, self.n_error = (
            self.fit.params["n"].value,
            self.fit.params["n"].stderr,
        )
        self.I_l, self.I_l_error = (
            self.fit.params["I_l"].value,
            self.fit.params["I_l"].stderr,
        )
        self.I_0, self.I_0_error = (
            self.fit.params["I_0"].value,
            self.fit.params["I_0"].stderr,
        )
        U_list_for_fit_plot = np.linspace(min(self.U_list), max(self.U_list), 100)
        self.fit_plot_list = [
            U_list_for_fit_plot,
            fitfunc(
                U_list_for_fit_plot,
                self.n,
                293,
                self.I_l,
                self.I_0,
                elementary_charge,
                Boltzmann,
            ),
        ]

    def slope_calc(self):
        """Calculates slope for getting approximate starting values"""
        linecalc = linregress(self.U_zero_list[-5:], self.U_list[-5:])
        self.intercept = linecalc[1]
        self.slope = linecalc[0]
        self.x = self.U_zero_list[-1:]
        self.slope_height = mean(self.U_list[-5:])

    def max_power_point(self):
        """Finds maximum power value and where it is in the list"""
        self.maximum_power = max(self.P_list)
        self.maximum_power_loc = self.P_list.index(self.maximum_power)
        print(
            self.U_list[self.maximum_power_loc],
            self.maximum_power,
            self.R_MOSFET_list[self.maximum_power_loc],
        )
        self.get_max_point = True

    def scan(self, nsteps, samplesize, begin=0, end=3.3, startvalues=False):
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
        Returns:
            list whit all the scan data
        """
        self.scan_data = []
        self.U_list = []
        self.I_list = []
        self.P_list = []
        self.U_err_list = []
        self.I_err_list = []
        self.P_err_list = []
        self.U_zero_list = []
        self.R_MOSFET_list = []
        self.R_MOSFET_err_list = []
        descent = False
        ascent = False
        for voltage in np.linspace(begin, end, nsteps):
            self.set_voltage(voltage)
            measurement = self.measure(samplesize)
            self.scan_data.append((voltage,) + measurement)
            u, i, p, r, u_err, i_err, p_err, r_err = measurement
            self.U_list.append(u)
            self.I_list.append(i)
            self.P_list.append(p)
            self.U_err_list.append(u_err)
            self.I_err_list.append(i_err)
            self.P_err_list.append(p_err)
            self.U_zero_list.append(voltage)
            self.R_MOSFET_list.append(r)
            self.R_MOSFET_err_list.append(r_err)
            if startvalues:
                if len(self.U_list) > 5:
                    self.slope_calc()
                    slope = self.slope

                    if slope < -1 and descent == False:
                        descent = True
                        startvalue = voltage + 0.02
                    elif descent == True and slope > -1 and ascent == False:
                        ascent = True
                        stopvalue = voltage - 0.13

        if startvalues:
            self.startvalue = startvalue
            self.stopvalue = stopvalue
        self.reset_out()
        if not startvalues:
            self.max_power_point()
        return self.scan_data

    def reset_out(self):
        """Sets the output of the device to 0"""
        self.device.turn_off()

    def csv_maker(self, filename):
        """Creates a csv file with the measurements and saves it under a unique name.
        Arguments:
            filename:
                A string containing the name of the csv and if necessary the path to save the file

        """

        if len(str.split(filename, ".csv")) == 1:
            filename = filename + ".csv"

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
                    "Mean voltage (V)",
                    "Mean current (A)",
                    "Mean Power (W)",
                    "R MOSFET (\u2126)",
                    "\u03B4 U (V)",
                    "\u03B4 I (A)",
                    "\u03B4 P (W)",
                    "\u03B4 R (\u2126)",
                ]
            )
            for measurement in self.scan_data:
                writer.writerow(measurement)

    def close_session(self):
        self.device.disconnect_device()


def listing():
    """Returns list of the devices connected to your computer.
    Arguments:

    Returns:
        List of connected ports"""
    ports = CD()

    return ports
