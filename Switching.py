import time

from crownstone_ble import CrownstoneBle
from crownstone_ble.Exceptions import BleError
from crownstone_core.Exceptions import CrownstoneBleException

from UART import DebugLogger
from Utils.PrintColors import *
from bluepy.btle import *

attempts = 1000
address = ''
failures = 0
devices = []
switchstate = False
starttime = time.time()

ble = CrownstoneBle()
ble.setSettings(
	'adminKeyForCrown',
	'memberKeyForHome',
	'basicKeyForOther',
	'MyServiceDataKey',
	'aLocalizationKey',
	'MyGoodMeshAppKey',
	'MyGoodMeshNetKey'
)


def switch():
	global switchstate
	try:
		ble.control.setSwitchState(switchstate)
		switchstate = not switchstate
		return 0
	except BTLEDisconnectError as err:
		return 1


def checkSetup():
	if not ble.isCrownstoneInNormalMode(address):
		yellow('Device is in setup mode')
		try:
			ble.setupCrownstone(
				address,
				crownstoneId=1,
				sphereId=1,
				meshDeviceKey='IamTheMeshKeyJey',
				ibeaconUUID='1843423e-e175-4af0-a2e4-31e32f729a8a',
				ibeaconMajor=123,
				ibeaconMinor=456
			)
		except CrownstoneBleException as err:
			if err.type == BleError.SETUP_FAILED:
				if ble.isCrownstoneInNormalMode(address):
					green('Setup completed!')
					return True
				else:
					return False
		return False
	else:
		# yellow('Device is in normal mode')
		# ble.connect(address)
		# ble.control.commandFactoryReset()
		# red('Reset done')
		return True


def disconnect():
	try:
		ble.disconnect()
		return 0
	except Exception as err:
		red(err)
		return 1


def connect():
	try:
		ble.connect(address)
		return 0
	except BTLEDisconnectError as err:
		red('Connecting failed', err)
		return 1


def scan():
	global address, devices

	devices = ble.getCrownstonesByScanning(2)
	for device in devices:
		if device['address'].startswith('ec:ac:'):
			# if not device['setupMode']:
			address = device['address']
			green('Found dev kit!')
			break


def switch_test():
	global logger

	# Connect to device
	blue('Start connecting')
	while connect() == 1:
		time.sleep(0.1)
	time.sleep(1)
	event = logger.get_event()
	if 'BLE_GAP_EVT_CONNECTED' in event:
		print('Crownstone BLE event: ', end='')
		red(event)
		green('->   We are connected!')
		blue('Done connecting\n')

	# Switch Crownstone
	blue('Sending switch command')
	switch()
	time.sleep(1)
	event = logger.get_event()
	if 'BLE_GATTS_EVT_WRITE' in event:
		print('Crownstone BLE event: ', end='')
		red(event)
		green('->   Switching is received!\n')

	# Disconnect from device
	blue('Start disconnecting')
	disconnect()
	time.sleep(1)

	while not logger.ble_event.endswith('DISCONNECTED'):
		time.sleep(0.1)

	# Wait for disconnected acknowledgement.
	event = logger.get_event()
	if 'BLE_GAP_EVT_DISCONNECTED' in event:
		print('Crownstone BLE event: ', end='')
		red(event)
		green('->   Disconnection successful')
		blue('Done disconnecting\n')
		yellow('Time: [', round(time.time() - starttime, 6), ']')
		blue('===============================================================\n')

	time.sleep(2)


if __name__ == '__main__':
	magenta('===============================================================')
	yellow('Time: [', round(time.time() - starttime, 6), ']')

	filename = 'UART_Switching.txt'
	testnumber = 10


	# Start UART connection.
	green('Debugger started...')
	logger = DebugLogger('Logger Thread', 1, filename)
	logger.start()

	green('Started scanning...')
	# Scan for devices
	scan()
	if not address > '':
		raise Exception('No address found!')

	green('Scanning done.')
	# Print address
	yellow('Found address:', address)
	# All devices
	# cyan("Found devices:", devices)

	# Check mode (setup/normal)
	cyan('Normal mode:', checkSetup())
	magenta('===============================================================')
	print('\n')

	cyan('Start switching')

	for i in range(1, testnumber + 1):
		cyan('Switch nr. ', i)
		try:
			switch_test()
		except:
			err = sys.exc_info()[0]
			if err == KeyboardInterrupt:
				raise
			if err == CrownstoneBleException:
				# Connection failed most likely, try again:
				i -= 1
			else:
				red('Error occurred:', err)

			# We caught exception, add to failure count.
			failures += 1

	cyan('Done\n\n')

	logger.exit_flag = True
	logger.join()

	cyan('\n\nUART Debugging saved to:', filename)

ble.shutDown()
