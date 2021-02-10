import subprocess as sp
import re
from time import time

from crownstone_ble import CrownstoneBle
from crownstone_ble.Exceptions import BleError
from crownstone_core.Exceptions import CrownstoneBleException

from Utils.UART import events
from Utils.UART import DebugLogger
from Utils.Colors.PrintColors import *
from bluepy.btle import *

# Some pre-defined variables
attempts = 1000
address = ''
failures = 0
devices = []
switchstate = 0
starttime = time.time()

# The Crownstone BLE object to communicate with Crownstones
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

# Extra variables regarding file output.
uart_connected = False
output_file = ""
out_file = False


# Function to write a line to the output file.
def output_to_file(line):
	"""
	This function will write a line to the output file for archival/debugging purposes.
	"""
	if output_file:
		with open(output_file, 'a') as f:
			f.write(line + '\n')


# Function to send a switch command to the Crownstone/dev-kit.
def switch():
	"""
	This function will send a switching command to the Crownstone and change the value of the
	"""
	global switchstate
	try:
		output_to_file("Switching...")
		# Send command
		ble.control.setSwitch(switchstate)
		# Change state
		if switchstate == 1:
			switchstate = 0
		else:
			switchstate = 1
		output_to_file("Switching done")
		return 0
	# Catch BTLEDisconnectError
	except BTLEDisconnectError as err:
		output_to_file("BTLEDisconnectError while switching")
		return 1


# Function to check if the device is in setup mode or not.
# If it is not, start setting it up with our keys.
def checkSetup():
	if not ble.isCrownstoneInNormalMode(address):
		yellow('Device is in setup mode')
		output_to_file("Device is in setup mode")
		try:
			output_to_file("Trying to setup crownstone")
			# Setup the Crownstone
			ble.setupCrownstone(
				address,
				crownstoneId=1,
				sphereId=1,
				meshDeviceKey='IamTheMeshKeyJey',
				ibeaconUUID='1843423e-e175-4af0-a2e4-31e32f729a8a',
				ibeaconMajor=123,
				ibeaconMinor=456
			)
			output_to_file("Setup complete")
		# Catch CrownstoneBleException
		except CrownstoneBleException as err:
			if err.type == BleError.SETUP_FAILED:
				# Setup most likely succeeded, but possible function returns fail, catch it with this.
				output_to_file("'SETUP_FAILED', likely still succeeded:")
				# So we check the normal mode again to make sure the setup did work.
				if ble.isCrownstoneInNormalMode(address):
					green('Setup completed!')
					output_to_file(">> Setup succeeded after all")
					return True
				else:
					return False
		return False
	else:
		# Nothing needs to be done and we can continue.
		# yellow('Device is in normal mode')
		# ble.connect(address)
		# ble.control.commandFactoryReset()
		# red('Reset done')
		output_to_file("Device is in normal mode")
		return True


# Function to disconnect from the device
def disconnect():
	"""
	Disconnects from the device and catches any exception that is thrown.
	"""
	try:
		ble.disconnect()
		return 0
	except Exception as err:
		red(err)
		output_to_file("Disconnect failed: " + err)
		return 1


# Function to scan for Crownstones, saves the address of the closest one for use.
def scan():
	"""
	This function will scan for the nearest Crownstone.
	It saves the address of this Crownstone
	"""
	global address, devices
	output_to_file("Scanning for devices")
	# devices = ble.getCrownstonesByScanning(2)
	device = ble.getNearestCrownstone()
	address = device['address']
	green('Found device"')
	output_to_file("Found device: " + address)


# Parse the UART message containing the Nordic BLE event
def checkNordicEvent(line):
	"""
	This function parses the Nordic event received over UART from the development board.
	"""
	# yellow(line) # Print out the line to check the event.

	# Split it in separate "words"
	parts = line.split(' ')
	# Ignore the first 2
	parts = parts[2:]
	# Filter
	event = re.sub('[^A-Za-z0-9]+', '', parts[1])
	# Return
	return events[event]


# The actual test, which executes the different parts.
def switch_test():
	"""
	The test first tries to connect with the device
	After that, it sends a command to the Crownstone to switch the relay.
	Once That is done, it will issue the disconnect command.

	If UART is enabled by connecting a development board via USB,
	it will use the output of that to check if the BLE messages are correctly received.
	"""
	global logger, uart_connected

	# Connect to device
	blue('Start connecting')
	output_to_file("Start connection")
	try:
		# Start connection
		ble.connect(address)
	except CrownstoneBleException as err:
		if err.type == BleError.COULD_NOT_VALIDATE_SESSION_NONCE:
			red("The closest Crownstone found is setup with different keys. Exiting...")
			import os
			# Quit the test, we found no Crownstone which is in setup mode or setup with our keys.
			os._exit(2)

		# We need to disconnect, otherwise, the program will keep trying with the incorrect data.
		disconnect()
		blue('===============================================================\n')
		# Wait until the disconnect is done.
		while address in sp.getoutput('hcitool con').lower().split():
			# green('Connected, according to hcitool!')
			pass
		return 1
	else:
		# We are connected
		# green('Connection complete!')
		output_to_file("Connection Complete")
		pass

	# Only execute if UART is connected.
	if uart_connected:
		# Wait for the logger to get a event (max 10 seconds to avoid lockup)
		t = time.time()
		while not logger.ble_event:
			if time.time() >= t + 10:
				# Did not receive switch command.
				return 1
			pass

		# Check if the event is the one we expect.
		event = checkNordicEvent(logger.get_event())
		if 'BLE_GAP_EVT_CONNECTED' in event:
			print('Crownstone BLE event: ', end='')
			red(event)
			green('->   We are connected!')
			blue('Done connecting\n')
			output_to_file("CONNECTED done on dev-kit")

	# Check the connection with the HCI tool
	if address in sp.getoutput('hcitool con').lower().split():
		green('Connected, according to hcitool!')
		output_to_file("hcitool con: Connected")

	# Switch Crownstone
	blue('Sending switch command')
	output_to_file("Starting Switching")
	# Switch command
	switch()

	# If UART is connected
	if uart_connected:
		# Wait for the logger to get a event (max 10 seconds to avoid lockup)
		t = time.time()
		while not logger.ble_event:
			if time.time() >= t + 10:
				# Did not receive switch command.
				return 1
			pass

		# Check event
		event = checkNordicEvent(logger.get_event())
		if 'BLE_GATTS_EVT_WRITE' in event:
			print('Crownstone BLE event: ', end='')
			red(event)
			green('->   Switch command is received!\n')
			output_to_file("SWITCHING done on dev-kit")

	# Disconnect from device
	blue('Start disconnecting')
	output_to_file("Starting Disconnecting")
	# Disconnect function
	disconnect()

	# If UART is connected
	if uart_connected:
		# Wait for the logger to get a event (max 10 seconds to avoid lockup)
		t = time.time()
		while not logger.ble_event:
			if time.time() >= t + 10:
				# Did not receive switch command.
				return 1
			pass

		# BLE event on development board
		event = checkNordicEvent(logger.get_event())
		# yellow(event)
		if event == 'BLE_GAP_EVT_DISCONNECTED':
			print('Crownstone BLE event: ', end='')
			red(event)
			green('->   Disconnection successful')
			blue('Done disconnecting\n')
			output_to_file("DISCONNECT done on dev-kit")

	t = time.time()
	while address in sp.getoutput('hcitool con').lower().split():
		if time.time() >= t + 10:
			# Connection was still live on our side
			output_to_file("ERROR: Connection still live on our side!")
			return 1
		# Still connected, so keep checking until disconnected.
		pass
	green('Disconnected, according to hcitool!')
	output_to_file("hcitool con: disconnected")

	# Calculate time it took this round.
	time_round = 'Time: [' + str(round(time.time() - starttime, 6)) +  ']'
	yellow(time_round)
	output_to_file(time_round)
	blue('===============================================================\n')

	return 0


if __name__ == '__main__':
	# Defaults
	testnumber = 100
	folder = '.'
	output_file = 'Switching_output.log'
	out_folder = False
	enable_scan = False
	debug = True
	# Launch arguments
	"""
	-a = Address
	-n = Number of tests
	-f = Output folder
	-w = Output file
	-o = Output to terminal or not
	-scan = Enable scanning
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
				enable_scan = False
			if i[0] == '-n':
				if i[1].isdigit:
					testnumber = int(i[1])
			if i[0] == '-f':
				cyan('Output folder:',  i[1])
				folder = i[1]
				sp.getoutput('mkdir ' + folder)
				out_folder = True
			if i[0] == '-w':
				cyan('Output file:', i[1])
				output_file = '/' + i[1]
				out_file = True
			if i[0] == '-o':
				debug = False if i[1] == '1' else True
			if i[0] == '-scan':
				enable_scan = False if i[1] == '0' else True
		if out_folder:
			output_file = './' + folder + '/' + output_file
		if out_file:
			with open(output_file, 'w'):
				pass

	# Quit if scanning is disabled AND no address is provided.
	if not enable_scan and len(address) < 17:
		red("Scanning is not enabled and/or address is not in the following format:\tXX:XX:XX:XX:XX:XX")
		yellow("Either add the '-a' argument with an address or use the '-scan' option")
		import os
		os._exit(1)

	magenta('===============================================================')
	blue("Amount of tests:", testnumber)
	blue("Scanning:", enable_scan)
	magenta('===============================================================')
	if not debug: sys.stdout = open(os.devnull, 'w')
	yellow('Time: [', round(time.time() - starttime, 6), ']')

	uart_file = folder + '/Switching_UART.txt'

	# Start UART connection.
	green("Starting debugger...")
	output_to_file("Starting debugger")
	logger = DebugLogger('Logger Thread', 1, uart_file)
	uart_connected = logger.connected_devices
	if uart_connected:
		logger.start()
		output_to_file("Started debugger")

	if enable_scan:
		green('Started scanning...')
		# Scan for devices
		scan()
		if not address > '':
			red('No address found!')
			quit()
		green('Scanning done.')
		output_to_file("Done scanning")

	# Print address
	blue('Address:', address)
	output_to_file("Address: " + address)
	# All devices
	# cyan("Found devices:", devices)

	# Check mode (setup/normal)
	cyan('Normal mode:', checkSetup())
	magenta('===============================================================')
	print()

	# Start looping for <testnumber> of times.
	for i in range(1, testnumber + 1):
		cyan('\nSwitch nr. ', i)
		output_to_file("Switch nr. " + str(i))
		try:
			failures += switch_test()
		except:
			err = sys.exc_info()[0]
			# print('ERROR', err)
			if err == KeyboardInterrupt:
				quit()
			else:
				red('Error occurred:', err)
				output_to_file("Error occurred: " + err)
	sys.stdout = sys.__stdout__
	cyan('\n\nDone\n')
	output_to_file("Done")
	red('Failures:', failures, 'out of', testnumber)
	output_to_file("Failures: " + str(failures) + " out of " + str(testnumber))

	# If UART is connected
	if uart_connected:
		# Set the flag for the thread to notify end.
		logger.exit_flag = True
		# End the thread
		logger.join()

		# Print our final message
		cyan('\n\nUART Debugging saved to:', uart_file)
		output_to_file("UART file saved as " + uart_file)

# Shutdown the ble object.
ble.shutDown()
