import pyvisa as pv

rm = pv.ResourceManager("@py")
ports = rm.list_resources()
print(ports)

device = rm.open_resource(ports[0], read_termination="\r\n", write_termination="\n")
print(device.query("*IDN?"))
