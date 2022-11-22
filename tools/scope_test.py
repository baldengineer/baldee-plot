import pyvisa  # for scpi
import time    # for sleep
import signal  # for ctrl-c
import sys     # call to ping
import os      # for exit signal

rm = pyvisa.ResourceManager('@py')
#rm.list_resources()
#('ASRL1::INSTR', 'ASRL2::INSTR', 'GPIB0::12::INSTR')

#bald_func = rm.open_resource('USB0::0x1AB1::0x0588::DG1D130400455::INSTR')
#mxo4 = rm.open_resource('TCPIP::192.168.128.23::INSTR')
#hmc_smps = rm.open_resource('TCPIP::192.168.128.24::INSTR')
#hmc_smps = rm.open_resource('USB0::0x0AAD::0x0135::051909041::INSTR')


#inst = rm.open_resource('USB0::0x1AB1::0x0588::DG1D130400455::INSTR')
inst = mxo4 = rm.open_resource('TCPIP::192.168.128.23::INSTR')

#inst.read_termination = '\r\n'
#inst.write_termination = '\r\n'
inst.query_delay = 0.1
# inst.write("*IDN?")
# time.sleep(0.1)
# while True:
#    print(inst.read_bytes(1))
print(inst.query("*IDN?"))
