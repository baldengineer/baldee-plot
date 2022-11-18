import pyvisa  # for scpi
import time    # for sleep
import signal  # for ctrl-c
import sys     # call to ping
import os      # for exit signal
from quantiphy import Quantity  # for pretty print of eng units


rm = pyvisa.ResourceManager()
#rm.list_resources()
#('ASRL1::INSTR', 'ASRL2::INSTR', 'GPIB0::12::INSTR')

mxo4 = rm.open_resource('TCPIP::192.168.128.23::INSTR')
#inst.read_termination = '\r\n'
#inst.write_termination = '\r\n'
#inst.query_delay = 0.001
# inst.write("*IDN?")
# time.sleep(0.1)
# while True:
#    print(inst.read_bytes(1))

def send_command(inst, cmd, scpi_delay=0.5, debug=True):
	if (debug): print(cmd)
	inst.write(cmd)
	time.sleep(scpi_delay)
	print(str(inst.query("SYST:ERR?")))
	time.sleep(scpi_delay)
	print("---")
	return True

# basic scope setup
def setup_scope(inst):
	print(inst.query("*IDN?"))
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

def get_meas(inst):
	inst.write("SINGLE")
	time.sleep(0.1) # check OPC register to see if we're ready
	meas_value = inst.query("MEAS1:RES:ACT?") # ACTual is optional
	unit_str = "V"
	c2_ptp = Quantity(meas_value, unit_str)
	print(f"C2 PTP: {c2_ptp}")

	meas_value = inst.query("MEAS2:RES:ACT?") # ACTual is optional
	c4_ptp = Quantity(meas_value, unit_str)
	print(f"C4 PTP: {c4_ptp}")

	meas_value = inst.query("MEAS3:RES:ACT?") # ACTual is optional
	unit_str = "Hz"
	c2_freq = Quantity(meas_value, unit_str)
	print(f"Frequency: {c2_freq}")

setup_scope(mxo4)
get_meas(mxo4)
