import time  # for sleep

def wait_for_opc(inst, timeout=30):
	start = time.time()
	while True:
		# is Operation Complete stuck?
		try:
			if (inst.query("*OPC?").strip() == "1"):
				return True
		except:
			print("!",end='')

		# if we stay stuck for 30 seconds, bail
		if ((time.time() - start) > timeout):
			print("OPC Failed")
			return False
		#print(".")
		time.sleep(0.1)
	return True

def send_command(inst, cmd, scpi_delay=0.1, debug=False):
	if (debug): print(cmd.strip())
	inst.write(cmd)
	if (debug): print("---")
	return wait_for_opc(inst)

def scale_channel(inst, mg, channel, debug=False):
	#scale up
	counter = 0
	while True:
		counter = counter + 1
		if (debug): print (f"Scale UP Att #{counter}")

		inst.write("SINGLE")
		wait_for_opc(inst)

		volts_per_div = float(inst.query(f"CHAN{channel}:SCAL?").strip())
		current_pp    = float(inst.query(f"MEAS{mg}:RES:ACT?").strip())
		min_pp = volts_per_div * 2
		if(debug):
			print(f"Current Peak to Peak: {current_pp}")
			print(f"Volts Per Div       : {volts_per_div}")
			print(f"Min Peak to Peak    : {min_pp}")

		## keep it in the 20-80 range

		# scale up if necessary
		if (current_pp < min_pp):
			new_pp = (current_pp * 1.2) / 8
			send_command(inst, f"CHAN{channel}:SCAL {new_pp}", 0.1, debug)
			inst.write("SINGLE")
			wait_for_opc(inst)
			volts_per_div = float(inst.query(f"CHAN{channel}:SCAL?").strip())
			current_pp    = float(inst.query(f"MEAS{mg}:RES:ACT?").strip())
		else:
			break

		if (counter >= 10):
			break

	# scales down
	counter = 0
	while True:
		counter = counter + 1
		if (debug): print (f"Scale DOWN Att #{counter}")
		inst.write("SINGLE")
		wait_for_opc(inst)

		volts_per_div = float(inst.query(f"CHAN{channel}:SCAL?").strip())
		current_pp    = float(inst.query(f"MEAS{mg}:RES:ACT?").strip())
		max_pp = volts_per_div * 9
		if (debug):
			print(f"Current Peak to Peak: {current_pp}")
			print(f"Volts Per Div       : {volts_per_div}")
			print(f"Max Peak to Peak    : {max_pp}")

		if (current_pp > max_pp):
			new_pp = (current_pp * 2) / 10
			send_command(inst, f"CHAN{channel}:SCAL {new_pp}", 0.1, debug)
		else:
			break

		if (counter >= 10):
			break
	return
