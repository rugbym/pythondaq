import pyvisa as pv
import time
import matplotlib.pyplot as plt

"""Module to control the Arduino device.
Available class:
ArduinoVISADevice:
    contains basic control commands and a sweep functions
    to measure voltages from the arduino across a LED
    and make a plot
    
    Typical usage example:
    from controllers.arduino_device import ArduinoVISADevice
    port = "ASRL3::INSTR"
    device = ArduinoVISADevice(port=port)"""


class ArduinoVISADevice:
    """programma om verschillende taken met de arduino uit te voeren.

    Typical usage example:

    port = "ASRL3::INSTR"
    device = ArduinoVISADevice(port=port)
    voltageCH0 = device.get_output_voltage(channel=channel_number"""

    def __init__(self, port="ASRL3::INSTR"):
        """Inits ArduinoVISADevice with the name of the port:
        Args:
            port:
                A string, the name of the port, default is "ASRL3::INSTR"""
        self.port = port
        rm = pv.ResourceManager("@py")
        self.device = rm.open_resource(
            self.port, read_termination="\r\n", write_termination="\n"
        )

    def set_output_value(self, channel, value):
        """Sets output value of a channel to given value.
        Args:
            channel:
             an integer, being the number of channel you want changed
            value:
                integer from 0-1023, sets the voltage setting to this value"""
        self.outputchannel = channel
        self.last_output_val = value
        self.device.query(f"OUT:CH{channel} {value}")

    def set_output_voltage(self, channel, outvoltage):
        """Sets output value of a channel to given value.
        Args:
            channel:
             an integer, being the number of channel you want changed
            outvoltage:
                float from 0-3,3, sets the voltage setting to this voltage"""
        self.outputchannel = channel
        self.last_output_volt = outvoltage
        self.device.query(f"OUT:CH{channel}:VOLT {outvoltage}")

    def get_output_voltage(self, channel):
        """Prints and returns the set ouput voltage on the given channel."""
        voltage = self.device.query(f"OUT:CH{channel}:VOLT?")
        print(f"The output voltage on CH{channel} is: {voltage} Volt")
        return voltage

    def get_input_voltage(self, channel, Volts=True):
        """Prints and returns the measured voltage on the given channel."""
        voltage = self.device.query(f"MEAS:CH{channel}:VOLT?")
        print(f"The input voltage on CH{channel} is: {voltage} Volt")
        return voltage

    def turn_off(self):
        """Sets output voltage value on 0."""
        if self.outputchannel == None:
            self.outputchannel = 0
        self.device.query(f"OUT:CH{self.outputchannel} {0}")

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

            self.device.query("OUT:CH0 " + f"{n}")

            u_ch0 = float(self.device.query("OUT:CH0:VOLT?"))
            u_ch1 = float(self.device.query("MEAS:CH1:VOLT?"))
            val_ch2 = float(self.device.query("MEAS:CH2?"))
            u_ch2 = float(self.device.query("MEAS:CH2:VOLT?"))
            I = u_ch2 / 220
            V = u_ch1 - u_ch2
            self.currentlist.append(I), self.voltagelist.append(V)

            if print == True:
                print(f"{n} {u_ch0:0.2f} Volt {val_ch2} {u_ch2:0.2f} Volt")

        self.device.query(f"OUT:CH0 {self.last_output_val}")
        if plot == True:
            self.plot()

    def plot(self):
        """Plots the voltage vs the current"""
        plt.plot(self.voltagelist, self.currentlist)
        plt.xlabel("Voltage over LED (V)"), plt.ylabel("Current over LED (A)")
        plt.show()

    def knipperlicht(self, tijd=10):
        """Blinks the light.

        Blinks the light for a given time, default is 10 seconds of blinking.

        Args:
            time:
               The time in seconds of how long the light blinks"""
        begin = time.time()
        bezig = 0
        n = 700

        while bezig < tijd:
            self.device.query("OUT:CH0 " + f"{n}")
            time.sleep(0.01)
            bezig = time.time() - begin
            n += 1023

        # self.device.query(f"OUT:CH0 {self.last_output_val}")
