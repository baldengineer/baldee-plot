def connect_visa_mp730028(baud):
	dmm = rm.open_resource(instruments_development.dmm_id)
	dmm.baud_rate = baud
	dmm.query_delay = 0.1
	# dmm.read_termination = '\n'
	# dmm.write_termination = '\r\n'
	print(dmm.query('*IDN?'))
	return dmm

def main():
	dmm = connect_visa_mp730028()
	setup_dmm_mp730028(dmm)
	print("Done.")	

def setup_dmm_mp730028(inst, debug=False):
	print(inst.query("*IDN?"))
	#inst.write("*RST")
	# inst.write("*OPC")
	# time.sleep(0.1)
	# for x in range(0,5):
	# 	print(inst.query("*OPC?"))
	# 	time.sleep(0.1)
	#wait_for_opc(inst)
	#time.sleep(1)

	inst.write('FUNC1 "VOLT:DC"')
	#wait_for_opc(inst)
	inst.write('FUNC2 "NONE"')
	#wait_for_opc(inst)
	if (debug): print(inst.query("MEAS1?"))

def wait_for_opc(inst, timeout=30):
	print("MP730028 OPC not implemented!")
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
