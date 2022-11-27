import pyvisa  # for scpi
import time    # for sleep
from quantiphy import Quantity  # for pretty print of eng units

import instruments_development  # globals for VISA resource strings

rm = pyvisa.ResourceManager()
print(rm.list_resources())

def connect_visa_mp730028():
	dmm = rm.open_resource(instruments_development.dmm_id)
	dmm.baud_rate = 115200
	dmm.query_delay = 0.1
	print(dmm.query('*IDN?'))
	return dmm

def main():
	dmm = connect_visa_mp730028()
	setup_dmm_mp730028(dmm)
	print("Done.")	

def setup_dmm_mp730028(inst):
	#inst.write("*RST")
	# inst.write("*OPC")
	# time.sleep(0.1)
	# for x in range(0,5):
	# 	print(inst.query("*OPC?"))
	# 	time.sleep(0.1)
	#wait_for_opc(inst)
	#time.sleep(1)

	inst.write('FUNC1 "VOLT:DC"')
	#wait_for_opc(inst)
	inst.write('FUNC2 "NONE"')
	#wait_for_opc(inst)
	print(inst.query("MEAS1?"))

def wait_for_opc(inst, timeout=30):
	start = time.time()
	while True:
		# is Operation Complete stuck?
		try:
			if (inst.query("*OPC?").strip() == "1"):
				return True
		except:
			print("!",end='')

		# if we stay stuck for 30 seconds, bail
		if ((time.time() - start) > timeout):
			print("OPC Failed")
			return False
		#print(".")
		time.sleep(0.1)
	return True

if __name__ == '__main__':
	main()
