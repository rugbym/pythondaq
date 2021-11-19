import pyvisa as pv
import time
import matplotlib.pyplot as plt


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
        # return self.device

    def set_output_value(self, channel, value):
        """Sets output value of a channel to given value.
        Args:
            channel:
             an integer, being the number of channel you want changed
            value:
                integer from 0-1023, sets the voltage setting to this value"""
        self.last_output_val = value
        self.device.query(f"OUT:CH{channel} {value}")
        self.outputchannel = channel

    def get_output_voltage(self, channel):
        """Prints and returns the set ouput voltage on the given channel."""
        voltage = self.device.query(f"OUT:CH{channel}:VOLT?")
        print(f"The output voltage on CH{channel} is: {voltage} Volt")
        return voltage

    def get_input_voltage(self, channel):
        """Prints and returns the measured voltage on the given channel."""
        voltage = self.device.query(f"MEAS:CH{channel}:VOLT?")
        print(f"The input voltage on CH{channel} is: {voltage} Volt")
        return voltage

    def turn_off(self):
        """Sets output voltage value on 0."""
        self.device.query(f"OUT:CH{self.outputchannel} {0}")

    def sweep_waardes(self, plot=False, print=True):
        """Sweeps value settings and calculates amps and voltage.

        Sweeps value on output channel from 0 to 1024 and measures value over the LED component and the current through the resistor.
        Args:
            plot:
                set to True if you want to see a plot of the results, default is False
            print:
                set to True if you want a print of output value, voltage and measured value and voltage on channel 2, default is True"""
        self.spanninglijst = []
        self.stroomlijst = []
        for n in range(0, 1024):

            self.device.query("OUT:CH0 " + f"{n}")

            u_ch0 = float(self.device.query("OUT:CH0:VOLT?"))
            u_ch1 = float(self.device.query("MEAS:CH1:VOLT?"))
            val_ch2 = float(self.device.query("MEAS:CH2?"))
            u_ch2 = float(self.device.query("MEAS:CH2:VOLT?"))
            I = u_ch2 / 220
            V = u_ch1 - u_ch2
            self.stroomlijst.append(I), self.spanninglijst.append(V)

            if print == True:
                print(f"{n} {u_ch0:0.2f} Volt {val_ch2} {u_ch2:0.2f} Volt")

        self.device.query(f"OUT:CH0 {self.last_output_val}")
        if plot == True:
            self.plot()

    def plot(self):
        """Plots the voltage vs the current"""
        plt.plot(self.spanninglijst, self.stroomlijst)
        plt.show()

    def knipperlicht(self, time=10):
        """Blinks the light.

        Blinks the light for a given time, default is 10 seconds of blinking.

        Args:
            time:
               The time in seconds of how long the light blinks"""
        begin = time.clock()
        print(begin)
        bezig = 0
        n = 700
        while bezig < time:
            self.device.query("OUT:CH0 " + f"{n}")
            time.sleep(0.01)
            bezig = time.clock() - begin
            n += 1023

        self.device.query(f"OUT:CH0 {self.last_output_val}")
