from time import time, sleep
from bluepy import btle

bt_address = 'EC:AC:CA:42:36:EE'


def keep_connection():
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
tests = 1000
error_count = 0

for i in range(tests):
	try:
		start_time = time()
		keep_connection()
		end_time = time() - start_time - 20
		sum += end_time
		count += 1
		avg = round(sum / count, 3)
		# print('Time before disconnect:', round(end_time, 3), ', Average:', avg)
	except:
		error_count += 1

print("Average time after 20 seconds forceful disconnect:", round(avg, 3), " seconds")
print("Amount of errored connections:", error_count)
