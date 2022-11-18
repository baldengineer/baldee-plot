import pyvisa  # for scpi
import time    # for sleep
import signal  # for ctrl-c
import sys     # call to ping
import os      # for exit signal
from quantiphy import Quantity  # for pretty print of eng units

rm = pyvisa.ResourceManager()
#rm.list_resources()
#('ASRL1::INSTR', 'ASRL2::INSTR', 'GPIB0::12::INSTR')

hmc_smps = rm.open_resource('TCPIP::192.168.128.24::INSTR')

def send_command(inst, cmd, scpi_delay=0.1, debug=True):
	if (debug): print(cmd)
	inst.write(cmd)
	time.sleep(scpi_delay)
	print(str(inst.query("SYST:ERR?")))
	time.sleep(scpi_delay)
	print("---")
	return True

def setup_hmc_smps(inst):
	print(inst.query("*IDN?"))
	send_command(inst, "OUTP:MAST OFF")
	send_command(inst,"INST OUT1")
	send_command(inst,"OUTP:CHAN ON")
	send_command(inst,"INST OUT2")
	send_command(inst,"OUTP:CHAN ON")
	send_command(inst,"INST OUT3")
	send_command(inst,"OUTP:CHAN OFF")

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


setup_hmc_smps(hmc_smps)
set_hmc_output_parameters(hmc_smps, 6.00, 0.025)

