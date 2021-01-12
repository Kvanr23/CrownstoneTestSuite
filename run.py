import argparse
import os
import subprocess
from threading import Thread
import time

flag = False
files = []
name = ''


def test(name: str, strace: bool):
	global flag
	cmd = 'python3 ConnectAndCommand.py -n 1 -o %s_UART.txt' % name
	strace_cmd = 'strace -o %s_strace.txt ' % name + cmd
	proc = subprocess.Popen(strace_cmd, shell=True) if strace else subprocess.Popen(cmd, shell=True)
	pid, sts = os.waitpid(proc.pid, 0)
	files.append(name + '_UART.txt')
	files.append(name + '_strace.txt') if strace else None
	flag = True


btmon_proc = None


def btmon():
	global btmon_proc, name
	filename = name + "_btmon.log"
	cmd = 'btmon -w ' + filename

	btmon_proc = subprocess.Popen(cmd, shell=True)
	pid, sts = os.waitpid(btmon_proc.pid, 0)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'-n', '--name',
		help='Name for the files (without extension!)',
		required=True
	)
	parser.add_argument(
		'-s', '--strace',
		action='store_true',
		help='Turn on/off stracing.'
	)
	parser.add_argument(
		'-b', '--btmon',
		action='store_true',
		help='Turn on hcipacket sniffing'
	)
	args = parser.parse_args()

	testThread = Thread(target=test, args=(args.name, args.strace))
	testThread.start()
	if args.btmon:
		name = args.name
		btmonThread = Thread(target=btmon)
		btmonThread.start()
		files.append(name + '_btmon.log')
	else:
		pass

	while not flag:
		pass
	testThread.join()
	if args.btmon:
		subprocess.Popen.kill(btmon_proc)
		btmonThread.join()
	print(files)
	print(
		'''
Done!
		
Generated the following files:
		'''
	)
	for file in files:
		print(file)
