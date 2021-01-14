from time import time, sleep
from bluepy import btle
import matplotlib.pyplot as plt

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
avgs = []
count = 0
tests = 100
error_count = 0

for i in range(tests):
	try:
		start_time = time()
		keep_connected()
		end_time = time() - start_time - 20
		sum += end_time
		count += 1
		avg = round(sum / count, 3)
		avgs.append(avg)
		print(i, ': Time before disconnect:', round(end_time, 3), ', Average:', avg)
	except:
		print('error')
		error_count += 1

# plt.ylim(0, 2)
plt.plot(list(range(0, tests - error_count)), avgs)
plt.show()
print("Average disconnect time:", avg, ' sec')
