from threading import Thread
import serial
import subprocess as sp
from time import time
from datetime import datetime


class DebugLogger(Thread):
	"""
	Class for reading the debug of the devkit.
	Working as a separate thread.
	"""

	def __init__(self, threadName, threadId, filename):
		"""
		Initializes the object and tries to open
		"""
		Thread.__init__(self)
		self.threadName = threadName
		self.threadId = threadId
		self.serial_is_open = False
		self.debug, self.file, self.ble_event = None, None, None

		# Find ttyACM path: (Try with the first one)
		path = sp.getoutput('ls /dev/ttyACM*')
		if not path.startswith('/dev'):
			print("No UART device connected")
			self.connected_devices = False
			return
		else:
			print("UART:", path)
			self.connected_devices = True

		try:
			self.open_debug(path)  # Change this according to your device.
			self.serial_is_open = True
		except serial.serialutil.SerialException as err:
			print("Could not open serial port:", err)
			self.serial_is_open = False

		self.file_name = filename

	def open_debug(self, port):
		"""
		Opens a serial connection with the dev kit.
		"""
		self.debug = serial.Serial(
			port=port,
			baudrate=230400,
			rtscts=True
		)
		self.debug.close()
		self.debug.open()

	def parse_line(self, line):
		parsed = line.split('] ')
		msg = parsed[1]
		parsed.pop(0)

		if msg.startswith('BLE'):
			# print("BLE Event:", msg, flush=True)
			self.ble_event = msg

	def get_line(self):
		"""
		Gets a single line from the debug stream over UART/Serial.
		"""
		line = None
		while not line:
			line = self.debug.readline().decode('utf-8').strip()
			self.parse_line(line)
		return line

	def get_event(self):
		evt = self.ble_event
		self.ble_event = ''
		return evt

	def reopen_file(self):
		"""
		Reopens file for appending a new line.
		"""
		self.file = open(self.file_name, 'a')

	def close_file(self):
		"""
		Close the file.
		"""
		self.file.close()

	def write_line_to_file(self, line=None):
		"""
		Write a line to the file.
		"""
		self.reopen_file()
		if not line:
			line = self.get_line() + '\r\n'
		t = round(time() - self.starttime, 4)
		self.file.write('[' + str(t) + ']' + line + '\r\n')
		self.close_file()

	def run(self):
		"""
		Run function for the Thread class.
		Closes if 'exit_flag' is set to True.
		"""
		self.exit_flag = False
		self.file = open(self.file_name, 'w')
		self.starttime = time()
		self.write_line_to_file(str(datetime.now()))
		while not self.exit_flag:
			if self.serial_is_open:
				self.write_line_to_file()
			else:
				self.close_file()
		self.debug.close()
