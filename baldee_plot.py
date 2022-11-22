import pyvisa  # for scpi
import time    # for sleep
import signal  # for ctrl-c
import sys     # call to ping
import os      # for exit signal
from quantiphy import Quantity  # for pretty print of eng units

rm = pyvisa.ResourceManager('@py')
#rm.list_resources()
#('ASRL1::INSTR', 'ASRL2::INSTR', 'GPIB0::12::INSTR')

# Windows
# bald_func = rm.open_resource('USB0::0x1AB1::0x0588::DG1D130400455::INSTR')
# mxo4 = rm.open_resource('TCPIP::192.168.128.23::INSTR')
# #hmc_smps = rm.open_resource('TCPIP::192.168.128.24::INSTR')
# hmc_smps = rm.open_resource('USB0::0x0AAD::0x0135::051909041::INSTR')
# mcp_dmm = rm.open_resource('ASRL22')

# Ubuntu
bald_func = rm.open_resource('USB0::0x1AB1::0x0588::DG1D130400455\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00::INSTR')
#mxo4 = rm.open_resource('TCPIP::192.168.128.23::INSTR')
mxo4 = rm.open_resource('USB0::2733::407::1335.5050k04-200191::0::INSTR')
hmc_smps = rm.open_resource('TCPIP::192.168.128.24::INSTR')
#hmc_smps = rm.open_resource('USB0::0x0AAD::0x0135::051909041::INSTR')
mcp_dmm = rm.open_resource('ASRL/dev/ttyUSB0::INSTR')

# some instraments want a delay because they don't have an OPC query
# or I am not using OPC
bald_func.query_delay = 0.1
mxo4.query_delay = 0.1
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

def setup_scope(inst):
	print(inst.query("*IDN?").strip())
	send_command(inst,"SYSTem:DISPlay:UPDate ON")

	# measurements
	send_command(inst,"MEASUREMENT1:ENABLE OFF")
	send_command(inst,"MEASUREMENT1:SOURCE C2")
	send_command(inst,"MEASUREMENT1:MAIN PDELta")
	send_command(inst,"MEASUREMENT1:ENABLE ON")

	send_command(inst,"MEASUREMENT2:ENABLE OFF")
	send_command(inst,"MEASUREMENT2:SOURCE C4")
	send_command(inst,"MEASUREMENT2:MAIN PDELta")
	send_command(inst,"MEASUREMENT2:ENABLE ON")

	send_command(inst,"MEASUREMENT3:ENABLE OFF")
	send_command(inst,"MEASUREMENT3:SOURCE C2")
	send_command(inst,"MEASUREMENT3:MAIN FREQ")
	send_command(inst,"MEASUREMENT3:ENABLE ON")

def get_scope_meas(inst, voltage):
	inst.write("SINGLE")
	time.sleep(1) # check OPC register to see if we're ready

	meas1_value = inst.query("MEAS1:RES:ACT?") # ACTual is optional
	c2_ptp = Quantity(meas1_value, "V")
	#meas1_value = str(meas1_value).strip()
	#print(f"C2 PTP: {c2_ptp}")

	meas2_value = inst.query("MEAS2:RES:ACT?") # ACTual is optional
	c4_ptp = Quantity(meas2_value, "V")
	#meas2_value = str(meas2_value).strip()
	#print(f"C4 PTP: {c4_ptp}")

	meas3_value = inst.query("MEAS3:RES:ACT?") # ACTual is optional
	c2_freq = Quantity(meas3_value, "Hz")
	#meas3_value = str(meas3_value).strip()
	#print(f"Frequency: {c2_freq}")
	print(f"{voltage},{meas1_value.strip()},{meas2_value.strip()},{meas3_value.strip()}, ,{c2_freq}, {c2_ptp}, {c4_ptp}")

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

setup_scope(mxo4)
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

# input voltage
#step_size = 10
step_size = 3
#voltage_settings = [0.1, 0.5, 1, 2]
voltage_settings = [0.5, 1]
for voltage in voltage_settings:
	#print(f"Sweeping for {voltage} V")
	set_hmc_output_parameters(hmc_smps, 5.00, 0.025)

	func_output_voltage_cmd = f"VOLT {voltage}"
	send_command(bald_func,func_output_voltage_cmd)

	for frequency in range(int(10e3),int(100e3),int(step_size * 1e3)):
		func_command = "FREQ " + str(frequency)
		send_command(bald_func,func_command)
		time.sleep(0.25)
		get_scope_meas(mxo4, voltage)

	for frequency in range(int(100e3),int(1e6),int(step_size * 10e3)):
		func_command = "FREQ " + str(frequency)
		send_command(bald_func,func_command)
		time.sleep(0.25)
		get_scope_meas(mxo4, voltage)
		#time.sleep(0.5)

	for frequency in range(int(1e6),int(10e6),int(step_size * 100e3)):
		func_command = "FREQ " + str(frequency)
		send_command(bald_func,func_command)
		time.sleep(0.25)
		get_scope_meas(mxo4, voltage)
		#time.sleep(0.5)

send_command(hmc_smps,"OUTP:MAST OFF")
send_command(bald_func, "OUTP OFF")
send_command(bald_func, "SYST:LOC")

#bald_func.write("SYST:LOC")