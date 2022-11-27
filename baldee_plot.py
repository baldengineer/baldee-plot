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

# instrument ids from instruments.py
bald_func  = rm.open_resource(instruments.func_id)
mxo4_scope = rm.open_resource(instruments.scope_id)
hmc_smps   = rm.open_resource(instruments.ps_id)
mcp_dmm    = rm.open_resource(instruments.dmm_id)

# some instraments want a delay because they don't have an OPC query
# or I am not using OPC
#mxo4_scope.query_delay = 0.1
hmc_smps.query_delay = 0.1
mcp_dmm.query_delay = 0.1
bald_func.query_delay = 0.1

# Configure the sweep
# freq_step_size = 1   # Unnecessarily slow scanning mechanism
# input_vpp_steps = [0.250, 0.500, 1.00, 2.00]
freq_step_size = 30
input_vpp_steps = [0.5, 1] # can just be one voltage for input

# create csv file to capture results
csv_filename_str = f"captures/{time.strftime('%Y-%m-%d-%H-%M-%S')}.csv"


def main():
	setup_scope(mxo4_scope)
	setup_hmc_smps(hmc_smps)
	setup_bald_func_gen(bald_func)

	with open(csv_filename_str, 'w', newline='') as csvfile:
		sweep_input_voltage(mxo4_scope, csvfile)

	send_command(hmc_smps,"OUTP:MAST OFF")
	send_command(bald_func, "OUTP OFF")
	bald_func.write("SYST:LOC") # query for error puts it back into remote!

def send_command(inst, cmd, scpi_delay=0.01, debug=False):
	if (debug): print(cmd)
	inst.write(cmd)
	time.sleep(scpi_delay)
	error_str = str(inst.query("SYST:ERR?"))
	if (debug): prinvoltage_settingst(error_str)
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

	mxo4.send_command(inst, "*RST")
	if (mxo4.wait_for_opc(inst) == False):
		print("Preset MXO4 Failed")
		exit()
	mxo4.send_command(inst,"MEASUREMENT1:ENABLE ON")

	command_sequence = [
		"SYSTem:DISPlay:UPDate ON",

		"CHAN1:STATe OFF",
		"CHAN2:STATe ON",
		"CHAN4:STATe ON",
		"TRIGger:EVENt1:SOURce C2",

		"HDEFinition:BWIDth 20E6",
		"HDEFinition:STATe ON",

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

		"MEAS4:ENABLE OFF",
		"MEAS4:SOURCE C4,C2",
		"MEAS4:MAIN PHASE",
		"MEAS4:ENABLE ON",

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

	# print("Early Exit in Scope Setup")
	# exit()

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

	meas4_value = inst.query("MEAS4:RES:ACT?").strip()
	phase_diff = meas4_value

	print(f"{voltage},{meas1_value},{meas2_value},{meas3_value},{phase_diff},{c2_freq}, {c2_ptp}, {c4_ptp}")
	csv.writerow([voltage, meas3_value, meas1_value, meas2_value, meas4_value])

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


	
def sweep_input_voltage(inst, csvfile):
	## Sweep frequency with different input voltages
	bode_log = csv.writer(csvfile, delimiter=',', quotechar='\\', quoting=csv.QUOTE_MINIMAL)
	header_line = [f'Input Voltage Sweep: {input_vpp_steps}']
	#bode_log.writerow(header_line.replace(',',' '))
	bode_log.writerow(header_line)

	for voltage in input_vpp_steps:
		#print(f"Sweeping for {voltage} V")
		set_hmc_output_parameters(hmc_smps, 5.00, 0.025)

		func_output_voltage_cmd = f"VOLT {voltage}"
		send_command(bald_func,func_output_voltage_cmd)
		mxo4.scale_channel(inst, "1", "2")  # meas, channel

		time_base_scale = 0.25  # get enough cycles on screen for valid freq/phase meas
		for frequency in range(int(10e3),int(100e3),int(freq_step_size * 1e3)):
			func_command = "FREQ " + str(frequency)
			send_command(bald_func,func_command)
			#time.sleep(0.15)
			mxo4.send_command(inst, f"TIMEBASE:SCALE {((1/frequency) * time_base_scale)}")
			get_scope_meas(inst, bode_log, voltage)

		for frequency in range(int(100e3),int(1e6),int(freq_step_size * 10e3)):
			func_command = "FREQ " + str(frequency)
			send_command(bald_func,func_command)
			#time.sleep(0.15)
			mxo4.send_command(inst, f"TIMEBASE:SCALE {((1/frequency) * time_base_scale)}")
			get_scope_meas(inst, bode_log, voltage)
			#time.sleep(0.5)

		for frequency in range(int(1e6),int(10e6),int(freq_step_size * 100e3)):
			func_command = "FREQ " + str(frequency)
			send_command(bald_func,func_command)	
			#time.sleep(0.15)
			mxo4.send_command(inst, f"TIMEBASE:SCALE {((1/frequency) * time_base_scale)}")
			get_scope_meas(inst, bode_log, voltage)
			#time.sleep(0.5)

if __name__ == '__main__':
	main()

