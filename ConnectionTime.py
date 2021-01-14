from time import time, sleep
from bluepy import btle

bt_address = 'EC:AC:CA:42:36:EE'


def keep_connected():
	p = btle.Peripheral(deviceAddr=bt_address, addrType=btle.ADDR_TYPE_RANDOM, iface=0)
	while not p.getState() == 'disc':
		# Keep checking for live connection.
		pass
	# Confirm disconnection at our side.
	p.disconnect()
	return 1

sum = 0
avg = 0
count = 0
tests = 50

for i in range(tests):
	try:
		start_time = time()
		keep_connected()
		end_time = time() - start_time
		sum += end_time
		count += 1
		avg = round(sum / count, 3)
		print('Time before disconnect:', round(end_time, 3), ', Average:', avg)
	except:
		i -= 1
