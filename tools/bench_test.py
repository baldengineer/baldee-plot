import pyvisa  # for scpi
import time    # for sleep
import signal  # for ctrl-c
import sys     # call to ping
import os      # for exit signal

rm = pyvisa.ResourceManager('@py')
print(rm.list_resources())
#('ASRL1::INSTR', 'ASRL2::INSTR', 'GPIB0::12::INSTR')

#bald_func = rm.open_resource('USB0::0x1AB1::0x0588::DG1D130400455::INSTR')
#mxo4 = rm.open_resource('TCPIP::192.168.128.23::INSTR')
#hmc_smps = rm.open_resource('TCPIP::192.168.128.24::INSTR')
#hmc_smps = rm.open_resource('USB0::0x0AAD::0x0135::051909041::INSTR')
#inst = rm.open_resource('USB0::0x1AB1::0x0588::DG1D130400455::INSTR')

# ls /sys/bus/usb-serial/devices/ -ltrah

#'USB0::6833::1416::DG1D130400455\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00::0::INSTR'
#'USB0::2733::309::051909041::0::INSTR'

#bald_func = rm.open_resource('USB0::0x1AB1::0x0588::DG1D130400455::INSTR')
bald_func = rm.open_resource('USB0::0x1AB1::0x0588::DG1D130400455\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00::INSTR')
mxo4 = rm.open_resource('TCPIP::192.168.128.23::INSTR')
#hmc_smps = rm.open_resource('TCPIP::192.168.128.24::INSTR')
hmc_smps = rm.open_resource('USB0::0x0AAD::0x0135::051909041::INSTR')
mcp_dmm = rm.open_resource('ASRL/dev/ttyUSB0::INSTR')

devices = [bald_func, mxo4, hmc_smps, mcp_dmm]

for device in devices:
	#inst.read_termination = '\r\n'
	#inst.write_termination = '\r\n'
	device.query_delay = 0.1
	device.baud_rate = 115200
	print(device.query("*IDN?"))
	time.sleep(1)


#bald_func.read_termination = '\r\n'
#bald_func.write_termination = '\r\n'
# bald_func.query_delay = 0.1
# mxo4.query_delay = 0.1

# bald_func.write("*IDN?")
# time.sleep(0.1)
# while True:
#    print(bald_func.read_bytes(1))