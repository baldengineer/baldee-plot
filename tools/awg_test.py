import pyvisa
import time

awg_id = 'TCPIP0::192.168.128.29::3000::SOCKET'
#awg_id =  'TCPIP0::192.168.128.29::inst0::INSTR'

rm = pyvisa.ResourceManager()
#print(rm.list_resources())

awg = rm.open_resource(awg_id)
awg.read_termination = '\n'
awg.write_termination = '\n'
print(awg.query("*IDN?"))
print(awg.query("SOURCE1:FUNC:SHAPE?"))
print(awg.query("SOURCE1:VOLT:LEVEL:IMM:AMPL?"))
#[SOURce[1|2]]:VOLTage[:LEVel][:IMMediate][:AMPLitude]

#awg.write("OUTPUT1:STATE ON")
awg.write("OUTPUT1:STATE OFF")
awg.write("SOURCE1:FUNC:SHAPE SIN")
awg.write("SOURCE1:FREQ:FIX 10e6")
awg.write("SOURCE1:VOLT:LEVEL:IMM:AMPL 980e-3")
