from crownstone_ble import CrownstoneBle
from crownstone_core.Exceptions import CrownstoneBleException
from crownstone_ble.Exceptions import BleError
import bluepy
try:
	from termcolor import colored
except ImportError:
	print('Please install termcolor:\n\n\'pip install termcolor\'')

import time
from Utils.PrintColors import *

attempts = 20
scantime = 10
failures = 0
address = ''

# red('Red')
# green('Green')
# blue('Blue')
# yellow('Yellow')
# magenta('Magenta')
# cyan('Cyan')
# white('White')


def scanCrownstones():
	global attempts, failures, address
	# if attempts % 2 != 0:
	# 	red('attempts needs to be even!')
	# 	quit()
	for attempt in range(attempts):
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

		devices = ble.getCrownstonesByScanning()
		for device in devices:
			address = device['address']
			blue(address, ":\t", round(device['rssi']), ":\t", device['setupMode'])

			if device['setupMode']:
				cyan('In setupMode')
				try:
					try:
						ble.setupCrownstone(
							device['address'],
							crownstoneId=1,
							sphereId=1,
							meshDeviceKey='IamTheMeshKeyJey',
							ibeaconUUID='1843423e-e175-4af0-a2e4-31e32f729a8a',
							ibeaconMajor=123,
							ibeaconMinor=456
						)
					except bluepy.btle.BTLEDisconnectError as err:
						red(err)
				except CrownstoneBleException as err:
					if err.type == BleError.SETUP_FAILED:
						print(
							colored(err.type, 'red'),
							colored(', checking in 2 seconds if the crownstone is in normal mode.', 'green'),
							colored('(We need to give the crownstone a little more time)', 'cyan')
						)
						time.sleep(2)
						blue("Normal mode now:", ble.isCrownstoneInNormalMode(address))

			if not device['setupMode']:
				cyan('Not in setupMode')

				if ble.isCrownstoneInNormalMode(address):
					magenta('In Normal mode')
				else:
					ble.connect(address)

				ble.disconnect()
				yellow('Wait 5 sec for scan')
				time.sleep(5)
				try:
					ble.connect(device['address'])
				except bluepy.btle.BTLEDisconnectError as err:
					red(err)
					ble.connect(device['address'])

				# yellow('Connected to crwn')
				try:
					ble.control.commandFactoryReset()
				except CrownstoneBleException as err:
					if err.type == BleError.CAN_NOT_FIND_SERVICE:
						# red(err.type)
						red('The factory reset function could not find the service!')
						# We need to restart the crownstone!
						input('Please restart the crownstone! Press enter when done!')
						ble.control.commandFactoryReset()
				blue('Reset done')
				time.sleep(3)
				# yellow('Disconnecting from crwn')
				ble.disconnect()
				# yellow('Disconnected from crwn')

			time.sleep(5)
			print('\n')

		ble.shutDown()


scanCrownstones()
if failures == 0:
	green("No problems with scanning!")