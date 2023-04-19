def main():
	print("This goes no where and does nothing.")

def setup_dmm_mp750290(inst, debug=False):
	print(inst.query("*IDN?"))
	awg.read_termination = '\n'
	awg.write_termination = '\n'
#	print(inst.query("*IDN?"))
#	print(inst.query("SOURCE1:FUNC:SHAPE?"))
#	print(inst.query("SOURCE1:VOLT:LEVEL:IMM:AMPL?"))

	inst.write("OUTPUT1:STATE OFF")
	inst.write("SOURCE1:FUNC:SHAPE SIN")
	inst.write("SOURCE1:FREQ:FIX 10e6")
	inst.write("SOURCE1:VOLT:LEVEL:IMM:AMPL 980e-3")

	if (debug): 
		print(inst.query("SOURCE1:FUNC:SHAPE?"))
		print(inst.query("SOURCE1:VOLT:LEVEL:IMM:AMPL?"))

	return True


def wait_for_opc(inst, timeout=30):
	print("haven't checked if mp750290 supports OPC yet!")
	return False
	# start = time.time()
	# while True:
	# 	# is Operation Complete stuck?
	# 	try:
	# 		if (inst.query("*OPC?").strip() == "1"):
	# 			return True
	# 	except:
	# 		print("!",end='')

	# 	# if we stay stuck for 30 seconds, bail
	# 	if ((time.time() - start) > timeout):
	# 		print("MP730028 OPC Failed")
	# 		return False
	# 	#print(".")
	# 	time.sleep(0.1)
	# return True

if __name__ == '__main__':
	main()
