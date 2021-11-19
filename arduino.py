import pyvisa as pv
import time

rm = pv.ResourceManager("@py")
ports = rm.list_resources()
print(ports)

device = rm.open_resource(ports[0], read_termination="\r\n", write_termination="\n")
print(device.query("*IDN?"))

lijst = []
for n in range(0, 1024):

    device.query("OUT:CH0 " + f"{n}")
    raw_val_ch0 = n
    real_val_ch0 = raw_val_ch0 / 1024 * 3.3
    time.sleep(0.01)
    raw_val_ch2 = int(device.query("MEAS:CH2?"))
    real_val_ch2 = raw_val_ch2 / 1024 * 3.3
    print(f"{raw_val_ch0} {real_val_ch0:0.2f}V {raw_val_ch2} {real_val_ch2:0.2f}V")

device.query("OUT:CH0 0")
