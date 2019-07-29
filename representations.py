from instructions import *

def flat(s):
	"""Convert process into flat list of words representation"""
	# TODO refactor this to have all the length in the front, like in ye olden times
	# This makes checking for mutability easier
	keys = [len(s[KEYS])] + list(s[KEYS])

	code = []
	for instruction in s[CODE]:
		code += [len(instruction)]
		code += instruction

	data = []
	for d in s[DATA]:
		data += [len(d)]
		data += d

	return [len(s[HEADER])] + s[HEADER] + keys + [len(s[CODE])] + code + [len(s[DATA])] + data + [len(s[STACK])] + s[STACK]

def sharp(f):
	"""Convert flat representation to hierarchical representation"""
	index = 0
	def read():
		nonlocal index
		d = f[index]
		index += 1
		return d

	l = read()
	header = [read() for i in range(l)]

	l = read()
	keys = set([read() for u in range(l)])

	l = read()
	code = [[read() for j in range(read())] for i in range(l)]

	data = []
	l = read()
	for i in range(l):
		dl = read()
		data += [read() for j in range(dl)]

	l = read()
	stack = [read() for i in range(l)]

	s = [header, keys, code, data, stack]
	#print("RET", s)
	return s

def pretty(p):
	"""Pretty-print a process"""
	if isinstance(p[0], list):
		p = flat(p)
	#print(p)
	if not isinstance(p[0], list):
		p = sharp(p)
	h = p[HEADER]
	c = p[KEYS]
	numbers = [str(h[i]) for i in [H_REC, H_GAS, H_MEM, H_IP]]
	keys = [str(c)]
	head = "\t".join(numbers+keys)

	body = str(p[DATA])# str(p[CODE]) +
	return head + "\n" + body

def validate(sharp):
	"""Validate a sharp process"""
	firstlevel = isinstance(sharp, list) and isinstance(sharp[HEADER], list) and isinstance(sharp[KEYS], list)
	if not firstlevel:
		print("first")
		return False
	datacheck = isinstance(sharp[DATA], list) and all([isinstance(instr, list) and all([isinstance(i, int) and i>=0 for i in instr]) for instr in sharp[DATA]])
	if not datacheck:
		return False

	codecheck = isinstance(sharp[CODE], list) and all([isinstance(instr, list) and all([isinstance(i, int) and i>= 0 for i in instr]) for instr in sharp[CODE]])
	if not codecheck:
		return False

	stackcheck = isinstance(sharp[STACK], list) and all([isinstance(i, int) for i in sharp[STACK]])
	if not stackcheck:
		return False

	return True
