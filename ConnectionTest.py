import csv
import re
import time
from threading import Thread
import serial

from bluepy.btle import *
from strace import strace_mask, strace_connect

# Hardcoded MAC address for Development kit, change if needed.
# Scanner can change it automatically.
address = 'EC:AC:CA:42:36:EE'
exit_flag = False


# Just a function to print a progressbar, for visual reference of the progress.
def progressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
	"""
	Call in a loop to create terminal progress bar
	@params:
		iteration   - Required  : current iteration (Int)
		total       - Required  : total iterations (Int)
		prefix      - Optional  : prefix string (Str)
		suffix      - Optional  : suffix string (Str)
		decimals    - Optional  : positive number of decimals in percent complete (Int)
		length      - Optional  : character length of bar (Int)
		fill        - Optional  : bar fill character (Str)
		printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
	"""
	percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
	filledLength = int(length * iteration // total)
	bar = fill * filledLength + '-' * (length - filledLength)
	print(f'\r{prefix} |{bar}| {percent}% {suffix}', flush=True)
	# Print New Line on Complete
	if iteration == total:
		print()


class ScanDelegate(DefaultDelegate):
	'''
	Class for scanning devices, for use with Bluepy.
	'''
	def __init__(self, scan_name):
		'''
		Initiate as Scan Delegate
		'''
		self.scan_name = scan_name
		DefaultDelegate.__init__(self)

	def handleDiscovery(self, scanEntry, isNewDevice, isNew):
		'''
		When a new device is discovered,
		it will be checked if it is the right device (devkit).
		If it is, the address is saved.
		'''
		global address
		if isNewDevice:
			name = scanEntry.getValueText(8)
			if name == self.scan_name:
				address = scanEntry.addr
				print("Found devkit:", name, scanEntry.addr)


class DebugLogger(Thread):
	'''
	Class for reading the debug of the devkit.
	Working as a seperate thread.
	'''
	def __init__(self, threadName, threadId):
		'''
		Initializes the object and tries to open
		'''
		Thread.__init__(self)
		self.threadName = threadName
		self.threadId = threadId
		self.serial_is_open = False
		try:
			self.open_debug('/dev/ttyACM0') # Change this according to your device.
			self.serial_is_open = True
		except serial.serialutil.SerialException as e:
			print("Could not open serial port")
			self.serial_is_open = False
		self.file_name = "UART_Debug.txt"

	def open_debug(self, port):
		'''
		Opens a serial connection with the dev kit.
		'''
		self.debug = serial.Serial(
			port=port,
			baudrate=230400,
			rtscts=True
		)
		self.debug.close()
		self.debug.open()

	def get_line(self):
		'''
		Gets a single line from the debug stream over UART/Serial.
		'''
		line = None
		while not line:
			line = self.debug.readline().decode('utf-8').strip()
		return line

	def open_file(self):
		'''
		Create/Open a (new) file.
		Overwrites existing file if already exists.
		'''
		self.file = open(self.file_name, 'w')

	def reopen_file(self):
		'''
		Reopens file for appending a new line.
		'''
		self.file = open(self.file_name, 'a')

	def close_file(self):
		'''
		Close the file.
		'''
		self.file.close()

	def write_line_to_file(self, line=None):
		'''
		Write a line to the file.
		'''
		self.reopen_file()
		if not line:
			line = self.get_line() + '\r\n'
		self.file.write(line + '\r\n')
		self.close_file()

	def run(self):
		'''
		Run function for the Thread class.
		Closes if 'exit_flag' is set to True.
		'''
		global exit_flag
		self.open_file()
		while not exit_flag:
			if self.serial_is_open:
				self.write_line_to_file()
			else:
				self.close_file()
		self.debug.close()


class DevKit(Thread):
	'''
	DevKit class, as a thread as well.
	For scanning, connecting, disconnecting and reading/writing to Crownstones.
	'''
	def __init__(self):
		Thread.__init__(self)
		self.address = None

	def scan_devices(self):
		'''
		Function to scan for Crownstones.
		In this case, EC:AC: is the start of the devkit used to create this.
		The name the devkit/Crownstone has after it is turned on, is crwn (no capitals).
		'''
		scanner = Scanner().withDelegate(ScanDelegate('crwn'))
		try:
			devices = scanner.scan(5.0)
		except BTLEManagementError as e:
			print("Unable to scan due to: ", e)
			exit()
		for device in devices:
			if 'ec:ac:' in device.addr:
				return device.addr

	def get_characteristic(self):
		'''
		Get the characteristics for reading/writing a value.
		Currently set to the setup service and control characteristic.

		This will be changed to a different one.
		'''
		services = self.p.getServices()
		for service in services:
			# print(service.uuid)
			if str(service.uuid).startswith('24f10000'):
				chars = service.getCharacteristics()
				for char in chars:
					if str(char.uuid).startswith('24f1000c'):  # control characteristic
						return char.getHandle()

	def connect_DK(self):
		'''
		Connect devkit via BLE
		Checks the status of the connection right after.
		ADDR_TYPE_RANDOM is required to be able to connect to a Crownstone.
		'''
		self.p = Peripheral()
		print(self.address)
		strace_connect(self.address, ADDR_TYPE_RANDOM, 0)(self.p.connect)
		status = self.p.status()
		if status['state'] == 'conn':
			# Connection is live
			return 'CONNECTED'

	def disconnect_DK(self):
		'''
		Disconnect from the previously connected Crownstone
		Wait for x amount of seconds before continuing.
		'''
		strace_mask()(self.p.disconnect)

		# We need to wait some time to be sure we are disconnected.
		time.sleep(2.5)  # Average time it takes to disconnect from the crownstone

	def test_connection(self):
		'''
		Function to test the connection.
		Measures time as well, but that is not used at the moment.
		Steps:
			1. Connect to Crownstone
			2. Get the characteristic
			3. Write to this characteristic
			4. Read this value back
			5. Disconnect from the Crownstone

		TODO: Make value better checkable by changing it everytime we connect.
		'''
		starttime = time.time()
		roundtime = starttime - self.prevtime
		self.connect_DK()
		handle = self.get_characteristic()
		self.p.writeCharacteristic(handle, b'01')

		read_value = self.p.readCharacteristic(handle)

		self.disconnect_DK()
		self.prevtime = time.time()

	def redundancy_test(self, attempts):
		'''
		Loop the test for 'attempts' amount of time.
		Save the amount of failures and highest sequential failures.
		Also use progressbar function to print the progress of the test.
		'''
		global failure
		self.start_time = time.time()
		self.prevtime = self.start_time

		self.failures = 0
		self.last_was_failure = False
		self.sequential = 0
		self.highest_sequential = 0

		for attempt in range(0, attempts):
			progressBar(attempt, attempts, prefix='Progress:', suffix='Complete', length=50)

			if not self.last_was_failure:
				self.sequential = 0
			try:
				self.test_connection()
				self.last_was_failure = False
			except BTLEDisconnectError as exception:
				failure = True
				self.last_was_failure = True
				self.failures += 1
				self.sequential += 1
				if self.sequential > self.highest_sequential:
					self.highest_sequential = self.sequential
				print("Failed connection! Attempt:", attempt, "Error:", exception, flush=True)

		# Done, so finish up the progressbar to 100%
		progressBar(attempts, attempts, prefix='Progress:', suffix='Complete', length=50)

		# Print out stats
		percentage = self.failures / attempts * 100
		print(percentage, "% failure rate:", self.failures, "failures, with", attempts, "total attempts.")
		print("Highest sequential failures:", self.highest_sequential)

	def run(self):
		'''
		Thread start function.
		This function starts all parts of the tests
		'''
		# Print the address of the (first) found dev kit.
		print("Address:", self.scan_devices(), flush=True)
		global exit_flag, address
		self.address = address

		# Create a logger Thread.
		self.loggerThread = DebugLogger('DevKit-Logger', 2)
		# Start the thread
		self.loggerThread.start()
		# Wait 2 secs before starting the test to make sure the serial connection is up.
		time.sleep(2)

		# Start the test
		# Parameter attemps: The amount of tests that will be done.
		self.redundancy_test(attempts=100)

		# When done, print that we are done.
		print("Done, saving...")

		# Set flag so the logger can save it's last line to the file.
		exit_flag = True
		time.sleep(1)

		# Stop the Logger Thread.
		self.loggerThread.join()


# If this file is used as main file instead of imported, run it.
if __name__ == '__main__':
	# try:
		dk_test = DevKit()
		dk_test.start()
	# except Exception as e:
	# 	print("Something failed!", e)
