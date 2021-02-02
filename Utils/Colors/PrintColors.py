try:
	from termcolor import colored
	avail = True
except ImportError:
	avail = False
	# print('Please install termcolor:\n\n\'pip install termcolor\'')


reset = '\033[0m'


def grey(*args):
	string = ''
	for i in range(len(args)):
		if i != 0:
			string += ' '
			string += str(args[i])
		else:
			string += str(args[i])

	if avail:
		print(colored(string, 'grey'))
	else:
		print('\033[30m' + string + reset)



def red(*args):
	string = ''
	for i in range(len(args)):
		if i != 0:
			string += ' '
			string += str(args[i])
		else:
			string += str(args[i])

	if avail:
		print(colored(string, 'red'))
	else:
		print('\033[31m' + string + reset)


def green(*args):
	string = ''
	for i in range(len(args)):
		if i != 0:
			string += ' '
			string += str(args[i])
		else:
			string += str(args[i])

	if avail:
		print(colored(string, 'green'))
	else:
		print('\033[32m' + string + reset)


def yellow(*args):
	string = ''
	for i in range(len(args)):
		if i != 0:
			string += ' '
			string += str(args[i])
		else:
			string += str(args[i])

	if avail:
		print(colored(string, 'yellow'))
	else:
		print('\033[33m' + string + reset)


def blue(*args):
	string = ''
	for i in range(len(args)):
		if i != 0:
			string += ' '
			string += str(args[i])
		else:
			string += str(args[i])
	if avail:
		print(colored(string, 'blue'))
	else:
		print('\033[34m' + string + reset)


def magenta(*args):
	string = ''
	for i in range(len(args)):
		if i != 0:
			string += ' '
			string += str(args[i])
		else:
			string += str(args[i])

	if avail:
		print(colored(string, 'magenta'))
	else:
		print('\033[35m' + string + reset)


def cyan(*args):
	string = ''
	for i in range(len(args)):
		if i != 0:
			string += ' '
			string += str(args[i])
		else:
			string += str(args[i])

	if avail:
		print(colored(string, 'cyan'))
	else:
		print('\033[36m' + string + reset)


def white(*args):
	string = ''
	for i in range(len(args)):
		if i != 0:
			string += ' '
			string += str(args[i])
		else:
			string += str(args[i])

	if avail:
		print(colored(string, 'white'))
	else:
		print('\033[37m' + string + reset)

