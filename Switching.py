from crownstone_ble import CrownstoneBle
from crownstone_ble.Exceptions import BleError
from crownstone_core.Exceptions import CrownstoneBleException
import bluepy
import time
from Utils.PrintColors import *

attempts = 10
address = ''
failures = ''
devices = []
switchstate = False

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
	ble.control.setSwitchState(switchstate)
	switchstate = not switchstate


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
	ble.disconnect()


def connect():
	ble.connect(address)


def scan():
	global address, devices

	devices = ble.getCrownstonesByScanning(2)
	for device in devices:
		if device['address'].startswith('ec:ac:'):
		# if not device['setupMode']:
			address = device['address']
			green('Found dev kit!')
			break


if __name__ == '__main__':
	# Scan for devices
	scan()

	# Print address
	blue(address)
	red(devices)

	# Check mode
	green('Normal mode:', checkSetup())

	# Connect to device
	connect()
	# Toggle the device twice
	switch()
	time.sleep(2)
	switch()
	# Disconnect from device
	disconnect()


ble.shutDown()
