import subprocess as sp
import re

from crownstone_ble import CrownstoneBle
from crownstone_ble.Exceptions import BleError
from crownstone_core.Exceptions import CrownstoneBleException

from Utils.UART import events
from Utils.UART import DebugLogger
from Utils.Colors.PrintColors import *
from bluepy.btle import *

attempts = 1000
address = ''
failures = 0
devices = []
switchstate = 0
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
		ble.control.setSwitch(1)
		if switchstate == 1:
			switchstate = 0
		else:
			switchstate = 1
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
	if ble.connect(address) == False:
		red('Connecting failed:')
		return 1
	else:
		return 0


def scan():
	global address, devices

	devices = ble.getCrownstonesByScanning(2)
	for device in devices:
		if device['address'].startswith('ec:ac:'):
			# if not device['setupMode']:
			address = device['address']
			green('Found dev kit!')
			break


def checkNordicEvent(line):
	yellow(line)
	parts = line.split(' ')
	parts = parts[2:]
	event = re.sub('[^A-Za-z0-9]+', '', parts[1])
	return events[event]


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
		event = checkNordicEvent(logger.get_event())
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
		event = checkNordicEvent(logger.get_event())
		if 'BLE_GATTS_EVT_WRITE' in event:
			print('Crownstone BLE event: ', end='')
			red(event)
			green('->   Switch command is received!\n')

	# Disconnect from device
	blue('Start disconnecting')
	disconnect()
	if uart_connected:
		# Wait for disconnected acknowledgement.
		while not logger.ble_event:
			pass

		event = checkNordicEvent(logger.get_event())
		# yellow(event)
		if event == 'BLE_GAP_EVT_DISCONNECTED':
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
	# Defaults
	testnumber = 100
	folder = '.'
	file = 'Switching_output.log'
	debug = True
	"""
	-n = Number of tests
	-f = Output folder
	-w = Output file
	-o = Output to terminal or not
	"""
	args = sys.argv
	args.pop(0)
	pairs = []
	if len(args) > 1:
		for i in range(len(args)):
			if i % 2 == 0:
				pairs.append([args[i], args[i+1]])
		for i in pairs:
			if i[0] == '-a':
				address = i[1]
			if i[0] == '-n':
				if i[1].isdigit:
					testnumber = int(i[1])
			if i[0] == '-f':
				cyan('Output folder:',  i[1])
				folder = i[1]
			if i[0] == '-w':
				cyan('Output file:', i[1])
				file = i[1]
			if i[0] == '-o':
				debug = False if i[1] == '1' else True


	magenta('===============================================================')
	blue("Amount of tests:", testnumber)
	magenta('===============================================================')
	if not debug: sys.stdout = open(os.devnull, 'w')
	yellow('Time: [', round(time.time() - starttime, 6), ']')

	filename = folder + '/Switching_UART.txt'

	# Start UART connection.
	green("Starting debugger...")
	logger = DebugLogger('Logger Thread', 1, filename)
	uart_connected = logger.connected_devices
	if uart_connected:
		logger.start()

	if not address:
		green('Started scanning...')
		# Scan for devices
		scan()
		if not address > '':
			red('No address found!')
			quit()
		green('Scanning done.')

	# Print address
	yellow('Address:', address)
	# All devices
	# cyan("Found devices:", devices)

	# Check mode (setup/normal)
	cyan('Normal mode:', checkSetup())
	magenta('===============================================================')
	print()

	for i in range(1, testnumber + 1):
		cyan('\nSwitch nr. ', i)
		# try:
		failures += switch_test()
		# except:
		# 	err = sys.exc_info()[0]
		# 	print('ERROR', err)
		# 	if err == KeyboardInterrupt:
		# 		quit()
		# 	else:
		# 		red('Error occurred:', err)
	sys.stdout = sys.__stdout__
	cyan('\n\nDone\n')
	red('Failures:', failures, 'out of', testnumber)

	if uart_connected:
		logger.exit_flag = True
		logger.join()

		cyan('\n\nUART Debugging saved to:', filename)

ble.shutDown()
