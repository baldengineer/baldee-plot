import pyvisa

rm = pyvisa.ResourceManager()
mp_dmm = rm.open_resource('ASRL/dev/ttyUSB0')
#mp_dmm.query_delay = 0.1

mp_dmm.baud_rate = 115200

print(mp_dmm.query("*IDN?"))
print(mp_dmm.query("MEAS?"))