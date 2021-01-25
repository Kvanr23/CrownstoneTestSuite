import subprocess as sp
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

uart_connected = False


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
		red('Connecting failed:', err)
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
	global logger, uart_connected

	# Connect to device
	blue('Start connecting')
	if connect() == 1:
		# We need to disconnect, otherwise, the program will keep trying with the incorrect data.
		disconnect()
		blue('===============================================================\n')
		# Wait until the disconnect is done.
		while address in sp.getoutput('hcitool con').lower().split():
			green('Connected, according to hcitool!')
		return 1
	else:
		# We are connected
		# green('Connection complete!')
		pass
	if uart_connected:
		event = logger.get_event()
		if 'BLE_GAP_EVT_CONNECTED' in event:
			print('Crownstone BLE event: ', end='')
			red(event)
			green('->   We are connected!')
			blue('Done connecting\n')

	if address in sp.getoutput('hcitool con').lower().split():
		green('Connected, according to hcitool!')

	# Switch Crownstone
	blue('Sending switch command')
	switch()
	# Wait a second to make sure the command has arrived (We can also see this with the BLE_GATTS_EVT_WRITE from UART)
	time.sleep(1)
	if uart_connected:
		event = logger.get_event()
		if 'BLE_GATTS_EVT_WRITE' in event:
			print('Crownstone BLE event: ', end='')
			red(event)
			green('->   Switch command is received!\n')

	# Disconnect from device
	blue('Start disconnecting')
	disconnect()
	if uart_connected:
		wait = time.time()
		# This will keep checking if the UART says the crownstone has disconnected.
		while not logger.ble_event.endswith('DISCONNECTED'):
			if time.time() == wait + 20:
				red('No disconnected event on Crownstone within 10 seconds')

	if uart_connected:
		# Wait for disconnected acknowledgement.
		event = logger.get_event()
		if 'BLE_GAP_EVT_DISCONNECTED' in event:
			print('Crownstone BLE event: ', end='')
			red(event)
			green('->   Disconnection successful')
			blue('Done disconnecting\n')

	while address in sp.getoutput('hcitool con').lower().split():
		# Still connected, so keep checking until disconnected.
		pass
	green('Disconnected, according to hcitool!')

	yellow('Time: [', round(time.time() - starttime, 6), ']')
	blue('===============================================================\n')

	return 0


if __name__ == '__main__':
	magenta('===============================================================')
	yellow('Time: [', round(time.time() - starttime, 6), ']')

	filename = 'UART_Switching.txt'
	testnumber = 1


	# Start UART connection.
	green("Starting debugger...")
	logger = DebugLogger('Logger Thread', 1, filename)
	uart_connected = logger.connected_devices
	if uart_connected:
		logger.start()
	green('Started scanning...')
	# Scan for devices
	scan()
	if not address > '':
		red('No address found!')
		quit()

	green('Scanning done.')
	# Print address
	yellow('Found address:', address)
	# All devices
	# cyan("Found devices:", devices)

	# Check mode (setup/normal)
	cyan('Normal mode:', checkSetup())
	magenta('===============================================================')
	print()

	for i in range(1, testnumber + 1):
		cyan('\nSwitch nr. ', i)
		try:
			failures += switch_test()
		except:
			err = sys.exc_info()[0]
			print('ERROR', err)
			if err == KeyboardInterrupt:
				quit()
			else:
				red('Error occurred:', err)

	cyan('Done\n\n')
	red('Failures:', failures, 'out of', testnumber)

	if uart_connected:
		logger.exit_flag = True
		logger.join()

		cyan('\n\nUART Debugging saved to:', filename)

ble.shutDown()
