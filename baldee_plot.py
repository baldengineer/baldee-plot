import pyvisa  # for scpi
import time    # for sleep
import signal  # for ctrl-c
import sys     # call to ping
import os      # for exit signal
from quantiphy import Quantity  # for pretty print of eng units
import csv     # for comma sep file

from insts import instruments  # globals for VISA resource strings
from insts import mxo4

rm = pyvisa.ResourceManager()
#rm.list_resources()
#('ASRL1::INSTR', 'ASRL2::INSTR', 'GPIB0::12::INSTR')

# bald_func = rm.open_resource('USB0::0x1AB1::0x0588::DG1D130400455\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00::INSTR')
# mxo4 = rm.open_resource('USB0::2733::407::1335.5050k04-200191::0::INSTR')
# hmc_smps = rm.open_resource('TCPIP::192.168.128.24::INSTR')
# mcp_dmm = rm.open_resource('ASRL/dev/ttyUSB0::INSTR')

bald_func  = rm.open_resource(instruments.func_id)
mxo4_scope = rm.open_resource(instruments.scope_id)
hmc_smps   = rm.open_resource(instruments.ps_id)
mcp_dmm    = rm.open_resource(instruments.dmm_id)

# some instraments want a delay because they don't have an OPC query
# or I am not using OPC
bald_func.query_delay = 0.1
mxo4_scope.query_delay = 0.1
hmc_smps.query_delay = 0.1
mcp_dmm.query_delay = 0.1

def send_command(inst, cmd, scpi_delay=0.01, debug=False):
	if (debug): print(cmd)
	inst.write(cmd)
	time.sleep(scpi_delay)
	error_str = str(inst.query("SYST:ERR?"))
	if (debug): print(error_str)
	time.sleep(scpi_delay)
	#if (debug): print("---")
	return True

def setup_bald_func_gen(inst):
	# TODO: Clear the error queue
	print(inst.query("*IDN?").strip())
	send_command(inst,"OUTP OFF")

	send_command(inst,"OUTP:LOAD INF")
	send_command(inst,"FUNC SIN")
	send_command(inst,"VOLT:UNIT VPP")
	send_command(inst,"VOLT 0.5")
	send_command(inst,"VOLT:OFFS 0")
	send_command(inst,"PHAS 0")

	send_command(inst,"OUTP ON")
	# go back to local mode
	# so baldee can touch the buttons
	#send_command("SYST:LOC")

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

		""
	]
	try: 
		for cmd in command_sequence:
			if (mxo4.send_command(inst, cmd) == False):
				print(f"'{cmd}' failed.")
				exit()
	except Exception as e:
		print(str(e))
		print("Failed to setup MXO4")
		exit()

def get_scope_meas(inst, csv, voltage):
	mxo4.send_command(inst,"SINGLE",0.1,False)

	mxo4.scale_channel(inst, "2", "4")

	meas1_value = inst.query("MEAS1:RES:ACT?").strip() # ACTual is optional
	c2_ptp = Quantity(meas1_value, "V")
	#meas1_value = str(meas1_value).strip()
	#print(f"C2 PTP: {c2_ptp}")

	meas2_value = inst.query("MEAS2:RES:ACT?").strip() # ACTual is optional
	c4_ptp = Quantity(meas2_value, "V")
	#meas2_value = str(meas2_value).strip()
	#print(f"C4 PTP: {c4_ptp}")

	meas3_value = inst.query("MEAS3:RES:ACT?").strip() # ACTual is optional
	c2_freq = Quantity(meas3_value, "Hz")
	#meas3_value = str(meas3_value).strip()
	#print(f"Frequency: {c2_freq}")
	print(f"{voltage},{meas1_value},{meas2_value},{meas3_value}, ,{c2_freq}, {c2_ptp}, {c4_ptp}")
	csv.writerow([voltage, meas3_value, meas1_value, meas2_value])

def setup_hmc_smps(inst):
	# for i in range(1,4):
	# 	try:
	# 		print(inst.query("SYSTEM:ERROR?"))
	# 	except:
	# 		print(f"Failed HMC {i} times")
	# 	time.sleep(0.5)
	print(inst.query("*IDN?").strip())
	send_command(inst, "OUTP:MAST OFF", 0.5)
	send_command(inst,"INST OUT1", 0.5)
	send_command(inst,"OUTP:CHAN ON", 0.5)
	send_command(inst,"INST OUT2", 0.5)
	send_command(inst,"OUTP:CHAN ON", 0.5)
	send_command(inst,"INST OUT3", 0.5)
	send_command(inst,"OUTP:CHAN OFF", 0.5)

def set_hmc_output_parameters(inst,volt_setting=5.55, curr_setting=0.005):
	hmc_voltage_cmd = f"VOLT {volt_setting}"
	hmc_current_cmd = f"CURR {curr_setting}"
	send_command(inst, "OUTP:MAST OFF")
	send_command(inst,"INST OUT1")
	send_command(inst,hmc_voltage_cmd)
	send_command(inst,hmc_current_cmd)
	send_command(inst,"INST OUT2")
	send_command(inst,hmc_voltage_cmd)
	send_command(inst,hmc_current_cmd)
	send_command(inst, "OUTP:MAST ON")

setup_scope(mxo4_scope)
setup_hmc_smps(hmc_smps)
setup_bald_func_gen(bald_func)


# step through some frequencies

######## Tried to 3 different VCCs (+/-)
# for voltage in [5.0,10.0,15.0]:
# 	#print(f"Sweeping for {voltage} V")
# 	set_hmc_output_parameters(hmc_smps, voltage, 0.025)
# 	for frequency in range(int(10e3),int(100e3),int(10e3)):
# 		func_command = "FREQ " + str(frequency)
# 		send_command(bald_func,func_command)
# 		time.sleep(0.25)
# 		get_scope_meas(mxo4, voltage)

# 	for frequency in range(int(100e3),int(1e6),int(100e3)):
# 		func_command = "FREQ " + str(frequency)
# 		send_command(bald_func,func_command)
# 		time.sleep(0.25)
# 		get_scope_meas(mxo4, voltage)
# 		#time.sleep(0.5)

# 	for frequency in range(int(1e6),int(10e6),int(1e6)):
# 		func_command = "FREQ " + str(frequency)
# 		send_command(bald_func,func_command)
# 		time.sleep(0.25)
# 		get_scope_meas(mxo4, voltage)
# 		#time.sleep(0.5)

# print("Early exit")
# exit()

# creat
filename_str = f"captures/{time.strftime('%Y-%m-%d-%H-%M-%S')}.csv"
with open(filename_str, 'w', newline='') as csvfile:
	bode_log = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	# input voltage
	#step_size = 10
	step_size = 30
	#voltage_settings = [0.1, 0.5, 1, 2]
	voltage_settings = [0.5, 1]

	for voltage in voltage_settings:
		#print(f"Sweeping for {voltage} V")
		set_hmc_output_parameters(hmc_smps, 5.00, 0.025)

		func_output_voltage_cmd = f"VOLT {voltage}"
		send_command(bald_func,func_output_voltage_cmd)
		mxo4.scale_channel(mxo4_scope, "1", "2")  # meas, channel

		time_base_scale = 2
		for frequency in range(int(10e3),int(100e3),int(step_size * 1e3)):
			func_command = "FREQ " + str(frequency)
			send_command(bald_func,func_command)
			time.sleep(0.15)
			mxo4.send_command(mxo4_scope, f"TIMEBASE:SCALE {((1/frequency) * time_base_scale)}")
			get_scope_meas(mxo4_scope, bode_log, voltage)

		for frequency in range(int(100e3),int(1e6),int(step_size * 10e3)):
			func_command = "FREQ " + str(frequency)
			send_command(bald_func,func_command)
			time.sleep(0.15)
			mxo4.send_command(mxo4_scope, f"TIMEBASE:SCALE {((1/frequency) * time_base_scale)}")
			get_scope_meas(mxo4_scope, bode_log, voltage)
			#time.sleep(0.5)

		for frequency in range(int(1e6),int(10e6),int(step_size * 100e3)):
			func_command = "FREQ " + str(frequency)
			send_command(bald_func,func_command)	
			time.sleep(0.15)
			mxo4.send_command(mxo4_scope, f"TIMEBASE:SCALE {((1/frequency) * time_base_scale)}")
			get_scope_meas(mxo4_scope, bode_log, voltage)
			#time.sleep(0.5)

send_command(hmc_smps,"OUTP:MAST OFF")
send_command(bald_func, "OUTP OFF")
time.sleep(0.25) # return to local seems to be ingored if sent back to back
send_command(bald_func, "SYST:LOC")

#bald_func.write("SYST:LOC")