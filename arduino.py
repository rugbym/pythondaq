import pyvisa as pv
import time
import matplotlib.pyplot as plt

rm = pv.ResourceManager("@py")
ports = rm.list_resources()
print(ports)

device = rm.open_resource(ports[0], read_termination="\r\n", write_termination="\n")
# print(device.query("*IDN?"))

spanninglijst = []
stroomlijst = []
for n in range(0, 1024):

    device.query("OUT:CH0 " + f"{n}")

    # time.sleep(0.01)
    raw_val_ch0, raw_val_ch1, raw_val_ch2 = (
        n,
        int(device.query("MEAS:CH1?")),
        int(device.query("MEAS:CH2?")),
    )
    real_val_ch0, real_val_ch1, real_val_ch2 = (
        raw_val_ch0 / 1024 * 3.3,
        raw_val_ch1 / 1024 * 3.3,
        raw_val_ch2 / 1024 * 3.3,
    )

    I = real_val_ch2 / 220
    V = real_val_ch1 - real_val_ch2
    stroomlijst.append(I), spanninglijst.append(V)

    # print(f"{raw_val_ch0} {real_val_ch0:0.2f}V {raw_val_ch2} {real_val_ch2:0.2f}V")

device.query("OUT:CH0 0")
plt.plot(spanninglijst, stroomlijst, "o")
plt.show()
