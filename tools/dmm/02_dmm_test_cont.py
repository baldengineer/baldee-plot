import pyvisa
from time import sleep

rm = pyvisa.ResourceManager()
mp_dmm = rm.open_resource('ASRL/dev/ttyUSB0')

mp_dmm.baud_rate = 115200

print(mp_dmm.query("*IDN?"))

while True: 
	print(mp_dmm.query("MEAS?").strip())
	sleep(1)
