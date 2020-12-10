try:
	from termcolor import colored
except ImportError:
	print('Please install termcolor:\n\n\'pip install termcolor\'')


def red(*args):
	string = ''
	for i in range(len(args)):
		if i != 0:
			string += ' '
			string += str(args[i])
		else:
			string += str(args[i])

	print(colored(string, 'red'))


def green(*args):
	string = ''
	for i in range(len(args)):
		if i != 0:
			string += ' '
			string += str(args[i])
		else:
			string += str(args[i])

	print(colored(string, 'green'))


def blue(*args):
	string = ''
	for i in range(len(args)):
		if i != 0:
			string += ' '
			string += str(args[i])
		else:
			string += str(args[i])

	print(colored(string, 'blue'))


def yellow(*args):
	string = ''
	for i in range(len(args)):
		if i != 0:
			string += ' '
			string += str(args[i])
		else:
			string += str(args[i])

	print(colored(string, 'yellow'))


def magenta(*args):
	string = ''
	for i in range(len(args)):
		if i != 0:
			string += ' '
			string += str(args[i])
		else:
			string += str(args[i])

	print(colored(string, 'magenta'))


def cyan(*args):
	string = ''
	for i in range(len(args)):
		if i != 0:
			string += ' '
			string += str(args[i])
		else:
			string += str(args[i])

	print(colored(string, 'cyan'))


def white(*args):
	string = ''
	for i in range(len(args)):
		if i != 0:
			string += ' '
			string += str(args[i])
		else:
			string += str(args[i])

	print(colored(string, 'white'))

