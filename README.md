# CrownstoneTestSuite
Testsuite for Crownstones

---

## NOTE:
This suite is built for Linux based operating systems because it relies on BlueZ and other Linux parts.

Therefore, don't try to run this on Windows, it will not work!

The test is runnable in a terminal or shell. May require `sudo` rights.

### Install bluepy!
In order to work, you need to install bluepy by IanHarvey:

####[Bluepy installation](https://www.github.com/IanHarvey/bluepy#installation)

---

## Usage:

`python3 ConnectionTest.py`

If you are getting the following response (or a similar 'permission denied' error):

`Unable to scan due to:  Failed to execute management command 'le on' (code: 20, error: Permission Denied)`

Please use `sudo`, on some Linux based Distro's, sudo is required for Bluetooth Low Energy.

`sudo python3 ConnectionTest.py`

### Commandline options

The script comes with some commandline options to change some settings, these can be viewed with the following:
`python3 ConnectionTest.py -h` or `--help`

###### Which will show:

```usage: ConnectionTest.py [-h] [-n NUMBER] [-u] [-d] [-o OUTPUTFILE]

optional arguments:
  -h, --help            show this help message and exit
  -n NUMBER, --number NUMBER
                        The amount of times the test should run.
  -u, --no_uart         To turn off UART logging. (-o, -d will be disabled.
  -d, --debug           Turns on debug messages, unsuccessful connections are still shown, progress is not.
  -o OUTPUTFILE, --outputfile OUTPUTFILE
                        The outputfile of the UART connection. Default is 'UART_Debug.txt'.
```

---

#### strace
The `ConnectionTest` can be used in combination with `strace`.

`strace` is a function to trace system calls within
It's best to do this with sudo, as some things will not show up.
You can let strace print everything out in the terminal you are running it in, or you can let it save it to a file with the `-o` parameter

`sudo strace -o [FILE_NAME] python3 ConnectionTest.py`
This will save everything in the `[FILE_NAME]` file.

---

#### BTMON
It is useful to run `btmon` in a separate terminal, so you can log the hci packets going to and from the Bluetooth controller.
You can do this with the following command:

`btmon -w [FILE_NAME.log]` 

This will continue until you cancel it with `ctrl+c` (or close the terminal :stuck_out_tongue_winking_eye:)

If `sudo` is required, either put sudo in front of it, or give `btmon` the right capabilities.

###### Sudo
`sudo btmon -w [FILE_NAME.log]`

###### Capabilities
`sudo setcap cap_net_raw+ep /usr/bin/btmon`

`/usr/bin/btmon` is the location for `btmon` on Ubuntu.

---