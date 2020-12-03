# This file is used to create a function which can be used to make "masks" or "notes" in a sTrace.
# This makes it easier to find faulty connections and what went wrong.

def strace_mask(*args):
	'''
	This function is for regular functions, of which you would like a mask in the sTrace.
	Usage:
		strace_mask(params)(function)
	'''
	def inner(function):
		def masker(args):
			try:
				open('function-%s-start' % function.__name__, 'r')
			except:
				pass
			function(*args)
			try:
				open('function-%s-end' % function.__name__, 'r')
			except:
				pass
		return masker(args)
	return inner


def strace_connect(deviceAddr, addrType, iface):
	'''
		This function is specifically for connecting BLE devices with Bluepy.
		Usage:
			strace_connect(deviceAddr, addrType, iface)(function)

		So if we have a Peripheral 'p' object with address 'AA:BB:CC:DD:EE:FF'
		and we want to use 'hci0', we would do the following:
			strace_connect('AA:BB:CC:DD:EE:FF', ADDR_TYPE_RANDOM, 0)(p.connect)
							^                   ^                 ^   ^
				         |  Address  | Random with Crownstone | hci | The connection function of Peripheral 'p'
	'''
	def inner(function):
		def masker(deviceAddr, addrType, iface):
			try:
				open('connection-deviceAddr-start', 'r')
			except:
				pass
			function(deviceAddr, addrType, iface)
			try:
				open('connection-deviceAddr-end', 'r')
			except:
				pass
		return masker(deviceAddr, addrType, iface)
	return inner