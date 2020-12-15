from threading import Thread
import serial


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
		self.debug, self.file = None, None
		try:
			self.open_debug('/dev/ttyACM0')  # Change this according to your device.
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
		parsed = line.split('')
		# print(parsed)
		source_file = parsed[0]
		msg = parsed[1][6:]
		parsed.pop(2)  # Unnecessary part of the string.

		if msg.startswith('BLE'):
			# print("MSG:", msg)
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
		self.file.write(line + '\r\n')
		self.close_file()

	def run(self):
		"""
		Run function for the Thread class.
		Closes if 'exit_flag' is set to True.
		"""
		self.exit_flag = False
		self.file = open(self.file_name, 'w')
		while not self.exit_flag:
			if self.serial_is_open:
				self.write_line_to_file()
			else:
				self.close_file()
		self.debug.close()
