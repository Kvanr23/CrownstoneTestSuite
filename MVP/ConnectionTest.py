from time import sleep
from bluepy import btle

timeout = 1
bt_address = 'EC:AC:CA:42:36:EE'
try:
	peripheral = btle.Peripheral(deviceAddr=bt_address, addrType=btle.ADDR_TYPE_RANDOM, iface=0)
	peripheral.disconnect()
except btle.BTLEDisconnectError as err:
	print(err)
	exit()
tests = 1000
error_counter = 0

for i in range(tests):
	if i/tests*100 % 10 == 0:
		print(i/tests*100, "%")
	try:
		peripheral.connect(addr=bt_address, addrType=btle.ADDR_TYPE_RANDOM, iface=0)
		if peripheral.status()['state'] == 'disc':
			print('Not connected')
		sleep(timeout)
		peripheral.disconnect()
		sleep(timeout)
	except btle.BTLEDisconnectError as err:
		error_counter += 1
		# print('A connection failed!')

print("Amount of failed connections:(total)\t", error_counter, "\t({total})".format(total=tests))
print("Percentage:\t", round(error_counter / tests * 100, 2), "%")

