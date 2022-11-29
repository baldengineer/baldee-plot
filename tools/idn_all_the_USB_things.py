import pyvisa  # for scpi
import time    # for sleep

rm = pyvisa.ResourceManager('@py')
#rm = pyvisa.ResourceManager('')
# print("Resource Manager says these things are available to play:")
# print(rm.list_resources())

instruments = rm.list_resources()

for inst in instruments:
	if (inst.startswith('USB')):
		this_resource = rm.open_resource(inst)
		this_resource.query_delay = 0.1 # some things like this
		this_resource.read_termination='\n'
		this_resource.write_termination='\n'
		print(f"\nTrying {inst}")
		try:
			print(this_resource.query("*IDN?"))
		except Exception as e:
			print(e)
		this_resource.close()
		time.sleep(1)
	else:
		print(f"Skipping {inst}")

rm.close()