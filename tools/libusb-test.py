import pyvisa  # for scpi

rm = pyvisa.ResourceManager('@py')
#rm = pyvisa.ResourceManager('')
print(rm.list_resources())

#inst = rm.open_resource('USB0::0x0AAD::0x0135::051909041::INSTR')
#inst = rm.open_resource('USB0::0x5345::0x1235::1930173::INSTR')
inst = rm.open_resource('ASRL24::INSTR')
#inst.query_delay = 0.1
#inst.baud_rate = 115200
print("Connected?")

print(inst.query("*IDN?"))
print("done")

inst.close()
rm.close()