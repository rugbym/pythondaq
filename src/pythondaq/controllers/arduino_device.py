try:
    from nsp2visasim import sim_pyvisa as pv
except ModuleNotFoundError:
    import pyvisa as pv
import time


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
    """Class to be able to perform different tasks with the Arduino device.

    Typical usage example:

    port = "ASRL3::INSTR"
    device = ArduinoVISADevice(port=port)
    voltageCH0 = device.get_output_voltage(channel=channel_number"""

    def __init__(self, port):
        """Inits ArduinoVISADevice with the name of the port:
        Args:
            port:
                A string, the name of the port, default is "ASRL3::INSTR"""
        self.port = port
        rm = pv.ResourceManager("@py")
        self.device = rm.open_resource(
            port, read_termination="\r\n", write_termination="\n"
        )

    def get_id_string(self):
        """Returns the device id"""
        return self.device.query("*IDN?")

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
        if __name__ == "__main__":
            print(f"The output voltage on CH{channel} is: {voltage} Volt")
        return voltage

    def get_input_voltage(self, channel):
        """Prints and returns the measured voltage on the given channel."""
        voltage = self.device.query(f"MEAS:CH{channel}:VOLT?")
        if __name__ == "__main__":
            print(f"The input voltage on CH{channel} is: {voltage} Volt")
        return voltage

    def get_input_value(self, channel):
        """Prints and returns the measured voltage on the given channel."""
        voltage = self.device.query(f"MEAS:CH{channel}?")
        if __name__ == "__main__":
            print(f"The input value on CH{channel} is: {voltage} ")
        return voltage

    def turn_off(self):
        """Sets output voltage value on 0."""
        if self.outputchannel == None:
            self.outputchannel = 0
        self.device.query(f"OUT:CH{self.outputchannel} {0}")

        # self.device.query(f"OUT:CH0 {self.last_output_val}")


def ConnectedDevs():
    """returns all connected ports"""
    rm = pv.ResourceManager("@py")
    return rm.list_resources()
