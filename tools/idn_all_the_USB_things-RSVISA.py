import time    # for sleep
import pyvisa  # for scpi

#rm = pyvisa.ResourceManager('@py')
rm = pyvisa.ResourceManager('')

instruments = rm.list_resources()
for inst in instruments:
	if (inst.startswith('USB')):
		this_resource = rm.open_resource(inst)
		this_resource.query_delay = 0.1 # some things like this
		print(f"\nTrying {inst}")
		try:
			print(this_resource.query("*IDN?").strip())
		except Exception as e:
			print(e)
		this_resource.close()
		time.sleep(1)
	else:
		print(f"Skipping {inst}")

rm.close()