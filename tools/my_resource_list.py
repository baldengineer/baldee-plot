import pyvisa  # for scpi

rm = pyvisa.ResourceManager('@py')
#rm = pyvisa.ResourceManager('')
print(rm.list_resources())
rm.close()