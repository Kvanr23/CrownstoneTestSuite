# Test Procedure

This is the procedure to take, in order to test the connections.

## Requirements
* Linux (It is built on Ubuntu)
* BlueZ (Tested and built with version 5.53, so results may vary with other versions)
* Python 3
* Installed BluePy
* Installed crownstone-lib-python-ble ([Installation](https://github.com/crownstone/crownstone-lib-python-ble#installing-crownstone-ble))
* Downloaded/Cloned this repository
* Bluenet v5.4.0 installed on a Crownstone/nRF52 devkit (connected via USB).

### Optional: nRF52 Development Board
If you have a development board with Bluenet installed on it, the UART bus over USB can be used. 
If it is connected, the test will use the output of the dev-board as confirmations. 
It will also generate a log file with everything from it.

## Sudo rights for Bluepy-helper

First find where bluepy-helper is located:
`python -m site`
This will return a list of paths, we need the dist-packages path.
This can be for example:
`/usr/local/lib/python3.8/dist-packages/`
The bluepy-helper will then be in:
`/usr/local/lib/python3.8/dist-packages/bluepy-1.3.0-py3.8.egg/bluepy/`

In order to set the sudo rights for it the following command is needed: 
`sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/local/lib/python3.8/dist-packages/bluepy-1.3.0-py3.8.egg/bluepy/bluepy-helper`
(Change the path if needed for different versions)
This will eliminate the need for sudo.

## Procedure

1. Open two terminals
2. On the first one, execute the following command: `btmon -w ./btmon.log`
3. In the second terminal, the test has to be run:
  `strace -o ./strace.log python3 Switching.py`
4. Wait until the test is done, when it is done, interrupt the `btmon` process with `ctrl+c` (`btmon` does not stop automatically)

---
#### This will result in 3 files:
* btmon.log
* strace.log

###### Optional
* UART_Switching.txt

##### What do these files contain?
* btmon.log can be opened in Wireshark
* strace.log contains all the systemcalls made during the test

###### Optional
* UART_Switching.txt contains all the information the Crownstone sent over the USB
---

## What next
Check the logs for which test number failed and check it in the UART log and the btmon in Wireshark.

# Optional arguments
* `-a <MAC ADDRESS>`: To skip scanning (if not added, there will be scanned for a (Crownstone) device with an address starting with `EC:`.
* `-n <NUMBER OF CONNECTIONS>`: To set a number of connections, the more connections, the accurater it will be. (Defaults to 100).
* `-f <FOLDER NAME>`: Puts generated files in this folder, it will create this folder if it does not exist.
* `-w <FILE NAME>`: File name to debug to, if not added, it will not create this file, will go in the same directory as `Switching.py` unless a folder is defined.



# TODO:
Start `btmon` from withing the script, so one terminal is needed.
