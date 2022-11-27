import pyvisa  # for scpi
import time    # for sleep
import signal  # for ctrl-c
import sys     # call to ping
import os      # for exit signal
from quantiphy import Quantity  # for pretty print of eng units
from instruments import scope_id as mxo4_id


# 20us/div

def main():
	global mxo4
	if (connect_to_VISA()):
		#setup_scope(mxo4)
		# for n in range(0,100):
		# 	get_meas(mxo4)
		# 	time.sleep(0.25)
		scale_channel(mxo4,"1","2")
		scale_channel(mxo4,"2","4")
	else:
		print("Connection to MXO4 Failed")
	exit()


def connect_to_VISA():
	global mxo4
	try:
		#rm = pyvisa.ResourceManager('@py')
		rm = pyvisa.ResourceManager()
		#rm.list_resources()
	except Exception as e:
		print(str(e))
		return False

	try:
		mxo4 = rm.open_resource(mxo4_id)
	except Exception as e:
		print(str(e))
		print(rm.list_resources())
		return False	
	return True

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

def send_command_mxo4(inst, cmd, scpi_delay=0.1, debug=True):
	if (debug): print(cmd.strip())
	inst.write(cmd)
	#time.sleep(scpi_delay)
	#print(str(inst.query("SYST:ERR?")))
	#time.sleep(scpi_delay)
	if (debug): print("---")
	return wait_for_opc(inst)

# basic scope setup
def setup_scope(inst):
	print(inst.query("*IDN?").strip())

	command_sequence = [
		"SYSTem:DISPlay:UPDate ON",
		"MEASUREMENT1:ENABLE OFF",
		"MEASUREMENT1:SOURCE C2",
		"MEASUREMENT1:MAIN PDELta",
		"MEASUREMENT1:ENABLE ON",

		"MEASUREMENT2:ENABLE OFF",
		"MEASUREMENT2:SOURCE C4",
		"MEASUREMENT2:MAIN PDELta",
		"MEASUREMENT2:ENABLE ON",

		"MEASUREMENT3:ENABLE OFF",
		"MEASUREMENT3:SOURCE C2",
		"MEASUREMENT3:MAIN FREQ",
		"MEASUREMENT3:ENABLE ON",
	]
	try: 
		for cmd in command_sequence:
			if (send_command_mxo4(inst, cmd) == False):
				print(f"'{cmd}' failed.")
				exit()
	except Exception as e:
		print(str(e))
		print("Failed to setup MXO4")
		exit()


maximum_vdiv = 100.00
minimum_vdiv = 0.005

def scale_channel(inst, mg, channel, debug=False):
	print(inst.query("*IDN?").strip())
	#send_command_mxo4(inst, f"CHAN{channel}:SCAL 0.150")

	#scale up
	counter = 0
	while True:
		counter = counter + 1
		if (debug): print (f"Scale UP Att #{counter}")

		inst.write("SINGLE")
		wait_for_opc(inst)

		volts_per_div = float(inst.query(f"CHAN{channel}:SCAL?").strip())
		current_pp    = float(inst.query(f"MEAS{mg}:RES:ACT?").strip())
		min_pp = volts_per_div * 2
		if(debug):
			print(f"Current Peak to Peak: {current_pp}")
			print(f"Volts Per Div       : {volts_per_div}")
			print(f"Min Peak to Peak    : {min_pp}")

		## keep it in the 20-80 range

		# scale up if necessary
		if (current_pp < min_pp):
			new_pp = (current_pp * 1.2) / 8
			send_command_mxo4(inst, f"CHAN{channel}:SCAL {new_pp}", 0.1, debug)
			inst.write("SINGLE")
			wait_for_opc(inst)
			volts_per_div = float(inst.query(f"CHAN{channel}:SCAL?").strip())
			current_pp    = float(inst.query(f"MEAS{mg}:RES:ACT?").strip())
		else:
			break

		if (counter >= 10):
			break

	# scales down
	counter = 0
	while True:
		counter = counter + 1
		if (debug): print (f"Scale DOWN Att #{counter}")
		inst.write("SINGLE")
		wait_for_opc(inst)

		volts_per_div = float(inst.query(f"CHAN{channel}:SCAL?").strip())
		current_pp    = float(inst.query(f"MEAS{mg}:RES:ACT?").strip())
		max_pp = volts_per_div * 9
		if (debug):
			print(f"Current Peak to Peak: {current_pp}")
			print(f"Volts Per Div       : {volts_per_div}")
			print(f"Max Peak to Peak    : {max_pp}")

		if (current_pp > max_pp):
			new_pp = (current_pp * 2) / 10
			send_command_mxo4(inst, f"CHAN{channel}:SCAL {new_pp}", 0.1, debug)
		else:
			break

		if (counter >= 10):
			break
	return

def get_meas(inst):
	try:
		inst.write("SINGLE")
		if (wait_for_opc(inst) == False):
			print("Trigger took longer than timeout")
			exit()
	except:
		exit()

	meas_value = inst.query("MEAS1:RES:ACT?") # ACTual is optional
	if (wait_for_opc(inst)):
		unit_str = "V"
		c2_ptp = Quantity(meas_value, unit_str)
		print(f"C2 PTP: {c2_ptp}")
	else:
		exit()

	meas_value = inst.query("MEAS2:RES:ACT?") # ACTual is optional
	if (wait_for_opc(inst)):
		c4_ptp = Quantity(meas_value, unit_str)
		print(f"C4 PTP: {c4_ptp}")
	else:
		exit()

	meas_value = inst.query("MEAS3:RES:ACT?") # ACTual is optional
	if (wait_for_opc(inst)):
		unit_str = "Hz"
		c2_freq = Quantity(meas_value, unit_str)
		print(f"Frequency: {c2_freq}")
	else:
		exit()

# I heard this was a good idea, but I forgot why
if __name__ == '__main__':
	main()

