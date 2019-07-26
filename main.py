#NAND machine?

def flatten(listoflists):
	return sum(listoflists, [])

WORDSIZE = 2**16

HEADER, CAPS, CODE, DATA = range(4)

# Add status flag for non-terminating failures?
HEADERLEN = 5
H_STATUS, H_REC, H_GAS, H_MEM, H_IP = range(HEADERLEN)

STATUSLEN = 6
S_NORMAL, S_OOC, S_OOG, S_OOM, S_OOA, S_OOF = range(STATUSLEN)
SNAMES = "S_NORMAL, S_OOC, S_OOG, S_OOM, S_OOA, S_OOF".split(", ")

NUMINSTR = 13
I_CREATE, I_ALLOC, I_TRANSFERCAP, I_RECURSE, I_MEMSIZE, I_MEMWRITE, I_MEMCREATE, I_ADD, I_SUB, I_JUMP, I_JUMPIF, I_CODEREAD, I_CODELEN = range(NUMINSTR)
INAMES = "I_CREATE, I_ALLOC, I_TRANSFERCAP, I_RECURSE, I_MEMSIZE, I_MEMWRITE, I_MEMCREATE, I_ADD, I_SUB, I_JUMP, I_JUMPIF, I_CODEREAD, I_CODELEN".split(", ")

ARGLEN = {
	I_CREATE: 1,
	I_ALLOC: 2,
	I_TRANSFERCAP: 2,
	I_RECURSE: 3,
	I_MEMSIZE: 1,
	I_MEMWRITE: 3,
	I_MEMCREATE: 0,
	I_ADD: 3,
	I_SUB: 3,
	I_JUMP: 1,
	I_JUMPIF: 3,
	I_CODEREAD: 3,
	I_CODELEN: 2,
}

IGASCOSTS = {
	I_CREATE: HEADERLEN,
	I_ALLOC: None,
	I_TRANSFERCAP: 6,
	I_RECURSE: 20,
	I_MEMSIZE: 1,
	I_MEMWRITE: 2,
	I_MEMCREATE: 4,
	I_ADD: 5,
	I_SUB: 5,
	I_JUMP: 2,
	I_JUMPIF: 5,
	I_CODEREAD: 8,
	I_CODELEN: 3,#TODO: mind flatten()
}

IMEMCOSTS = {
	I_CREATE : HEADERLEN,#plus some constant overhead for lists?
	I_ALLOC: None,
	I_TRANSFERCAP: None,
	I_RECURSE: 0,
	I_MEMSIZE: 0,
	I_MEMWRITE: 0,
	I_MEMCREATE: 2,
	I_ADD: 0,
	I_SUB: 0,
	I_JUMP: 0,
	I_JUMPIF: 0,
	I_CODEREAD: 0,
	I_CODELEN: 0,
}

def flat(s):
	# TODO refactor this to have all the length in the front, like in ye olden times
	# This makes checking for mutability easier
	caps = [len(s[CAPS])] + list(s[CAPS])

	code = []
	for instruction in s[CODE]:
		code += [len(instruction)]
		code += instruction

	data = []
	for d in s[DATA]:
		data += [len(d)]
		data += d

	return [len(s[HEADER])] + s[HEADER] + caps + [len(s[CODE])] + code + [len(s[DATA])] + data

def sharp(f):
	#print(f)
	index = 0
	def read():
		nonlocal index
		d = f[index]
		index += 1
		return d

	l = read()
	header = [read() for i in range(l)]

	l = read()
	caps = set([read() for u in range(l)])

	l = read()
	code = [[read() for j in range(read())] for i in range(l)]

	data = []
	l = read()
	for i in range(l):
		dl = read()
		data += [read() for j in range(dl)]

	s = [header, caps, code, data]
	#print("RET", s)
	return s

def pretty(p):
	if isinstance(p[0], list):
		p = flat(p)
	#print(p)
	if not isinstance(p[0], list):
		p = sharp(p)
	h = p[HEADER]
	c = p[CAPS]
	numbers = [str(h[i]) for i in [H_REC, H_GAS, H_MEM, H_IP]]
	caps = [str(c)]
	head = "\t".join(numbers+caps)

	body = str(p[DATA])# str(p[CODE]) +
	return head + "\n" + body

#allow for reduction of caps?

# does it always jump back to the minimum of all header resources?

def validate(sharp):
	firstlevel = isinstance(sharp, list) and isinstance(sharp[0], list) and isinstance(sharp[1], set) and isinstance(sharp[2], list)
	if not firstlevel:
		return False
	secondlevel = all([isinstance(instr, list) and all([isinstance(i, int) and i>=0 for i in instr]) for instr in sharp[2]])
	if not secondlevel:
		return False

	thirdlevel = all([isinstance(instr, list) and all([isinstance(i, int) and i>= 0 for i in instr]) for instr in sharp[3]])
	if not thirdlevel:
		return False

	return True

def run(code):
	#TODO: make CAPS dict? other data structure?
	process = [[S_NORMAL,0,1000,1000,0], {0}, code, []]

	if not validate(process):
		print("INTRO VALIDATE FAIL")
		exit(1)

	world = [process]

	def debug():
		print("\nSTEP#"	 + str(STEP), INAMES[I])
		for proc in world:
			print(pretty(proc))

	start = 0
	chain = [start]

	while True:
		current = chain[-1]
		rec = world[current][HEADER][H_REC]
		if rec != current:
			chain.append(rec)
		else:
			break

	#print("CHAIN", chain)
	#traverse H_REC here?

	STEP = 0
	while True:
		STEP += 1
		#print(STEP)
		# TODO add jump-back logic to last process in parent chain that has sufficient resources

		if len(chain) == 0:
			#print("END")
			return world
			#break
		this = world[chain[-1]]

		#if not validate(this):
			#jump_back(S_OOF)
			#continue
		#	os._exit(1)

		#TODO: only deserialize here, on demand

		header = this[HEADER]
		caps = this[CAPS]
		code = this[CODE]

		JB = False

		def jump_back(condition, to=None):
			nonlocal chain, JB
			JB = True
			header[H_STATUS] = condition
			# TODO make this nicer
			if to is None:
				#world[active] = flat(world[active])
				chain = chain[:-1]
			else:
				for i in range(len(world)-1, to, -1):
					#world[i] = flat(world[i])
					chain = chain[:-1]

		def set_cap(target):
			caps.add(target)

		def has_cap(target):
			return target in caps

		def transfer_cap(index, table):
			if index in caps:
				table.add(index)

		ip = header[H_IP]
		if ip >= len(code):#could also wrap around for shits and giggles
			jump_back(S_OOC)
			continue

		#print(ip, len(code))
		try:
			C = code[ip]
			I = C[0]
		except IndexError:
			jump_back(S_OOC)
			continue

		if I >= NUMINSTR:
			print("numinstr")
			jump_back(S_OOA)#TODO maybe other code here?
			continue

		#TODO check length
		args = C[1:]

		if len(args) != ARGLEN[I]:
			print("arglen")
			jump_back(S_OOA, len(chain)-2)
			continue

		gascost = IGASCOSTS[I]
		if gascost is None:
			gascost = args[1]#size arg for ALLOC

		memcost = IMEMCOSTS[I]
		if memcost is None:
			if I == I_ALLOC:
				memcost = args[1]#size arg for ALLOC
			elif I == I_TRANSFERCAP:
				memcost = sum([1 for c in args[1:] if c is not None])

		for node_index, node in enumerate(chain):
			node_header = world[node][HEADER]
			if not validate(world[node]):
				#TODO this is too heavy
				jump_back(S_OOF, node_index-1)
				break
			if node_header[H_GAS] < gascost:
				jump_back(S_OOG, node_index-1)
				break
			if node_header[H_MEM] < memcost:
				jump_back(S_OOM, node_index-1)
				break


		if JB:
			continue

		# First check all conditions, then change the state!
		for node_index, node in enumerate(chain):
			world[node][HEADER][H_GAS] -= gascost
			world[node][HEADER][H_MEM] -= memcost

		#debug()

		header[H_IP] += 1

		if I == I_CREATE:
			memory = args[0]
			index = len(world)

			try:
				newproc = sharp(this[DATA][memory])
			except IndexError:
				#TODO set STATUS
				continue
			newproc[HEADER] = [S_NORMAL, 0, 0, 0, 0]
			newproc[CAPS] = set()#TODO it's own call cap! (?)
			print("NEW", newproc)
			world.append(newproc)

			set_cap(index)

		elif I == I_ALLOC:
			memory, size = args
			try:
				this[DATA][memory] += [0 for i in range(size)]
			except IndexError:
				#TODO other code
				#print("index")
				jump_back(S_OOA, node_index-1)
				continue

		elif I == I_TRANSFERCAP:
			# TODO can only transfer 1 cap per call
			target, cap = args

			if has_cap(target):
				target_caps = world[target][CAPS]
				transfer_cap(cap, target_caps)

		elif I == I_RECURSE:
			target, gas, mem = args

			if has_cap(target):

				target_header = world[target][HEADER]
				target_header[H_GAS] = min(header[H_GAS], gas)
				target_header[H_MEM] = min(header[H_MEM], mem)

				header[H_REC] = target
				active = target
				chain.append(target)

		elif I == I_MEMSIZE:
			target_index = args[0]
			try:
				this[DATA][target_index] = len(this[DATA])#must be serialized!
			except IndexError:
				jump_back(S_OOA)
				#print("memsize")
				continue

		elif I == I_MEMWRITE:
			memory, address, data = args
			try:
				this[DATA][memory][address] = data
			except IndexError:
				#print("memwrite")
				jump_back(S_OOA)
				continue

		elif I == I_MEMCREATE:
			this[DATA].append([])

		elif I == I_ADD:
			memory, address1, address2 = args
			try:
				this[DATA][memory][address1] = (this[DATA][memory][address1]+this[DATA][memory][address2]) % WORDSIZE
			except IndexError:
				jump_back(S_OOA)
				continue

		elif I == I_SUB:
			memory, address1, address2 = args
			try:
				this[DATA][memory][address1] = (this[DATA][memory][address1]-this[DATA][memory][address2]) % WORDSIZE
			except IndexError:
				jump_back(S_OOA)
				continue

		elif I == I_JUMP:
			target = args[0]
			this[HEADER][H_IP] = target

		elif I == I_JUMPIF:
			target, memory, address = args
			try:
				if this[DATA][memory][address] > 0:
					this[HEADER][H_IP] = target
			except IndexError:
				jump_back(S_OOF)
				continue

		elif I == I_CODEREAD:
			code_index, memory, address = args
			try:
				this[DATA][memory][address] = flatten(this[CODE])[code_index]
			except IndexError:
				jump_back(S_OOA)
				continue

		elif I == I_CODELEN:
			memory, address = args
			try:
				this[DATA][memory][address] = len(flatten(this[CODE]))
			except IndexError:
				jump_back(S_OOA)
				continue

import json
import os
import sys

from time import time

from graphviz import Digraph

def visualize(world, startcode):

	dot = Digraph()
	dot.format = "svg"

	def name(index):
		header = world[index][HEADER]
		return "%i [%s|%i|%i|%s|%s]" % (index, SNAMES[header[H_STATUS]], header[H_GAS], header[H_MEM], str(world[index][CODE]), str(world[index][DATA]))

	#TODO highlight active
	if not isinstance(world[0][0], list):
		print("VIZ NOT SHARP")
		return

	edges = 0
	for pi, proc in enumerate(world):
		for cap in proc[CAPS]:
			edges += 1
			dot.edge(name(pi), name(cap), color="black")

	print(edges)
	#if edges > 3:# and len(edges) > len(world)-2:
	if True:
		fname = str(int(time()*10000))
		with open("graphs/"+fname+".txt", "w+") as f:
			f.write(startcode)
		dot.render("graphs/"+fname, view=True)

"""
from random import random, randint, choice

def small():
	return randint(0,8)

def big():
	return randint(0,32)

GEN = {
	I_CREATE: [small],
	I_ALLOC: [small, big],
	I_TRANSFERCAP: [small, small],
	I_RECURSE: [small, big, big],
	I_MEMSIZE: [small],
	I_MEMWRITE: [small, big, big],
	I_MEMCREATE: [],
	I_ADD: [small, big, big],
	I_SUB: [small, big, big],
	I_JUMP: [big],
	I_JUMPIF: [small, big, big],
}

def gencode():

	code = []

	for i in range(randint(10,50)):
		instr = randint(0, NUMINSTR-1)
		code.append([instr]+[f() for f in GEN[instr]])
	#print(code)
	return code

for i in range(10000):
	code = gencode()
	startcode = str(code)
	world = run(code)
	#print(code)
	#print(SNAMES[world[0][0][0]])
	visualize(world, startcode)
"""

"""

def main():
	try:
		data = sys.stdin.read()
		code = json.loads(data)
	except (UnicodeError, json.decoder.JSONDecodeError, RecursionError):
		os._exit(1)

	world = run(code)
	visualize(world, data)
	os._exit(0)

if __name__ == "__main__":
	import afl
	afl.start()
	main()
"""

#H_STATUS, H_REC, H_GAS, H_MEM, H_IP
code = [
[I_MEMCREATE],
[I_ALLOC, 0, 15],

[I_MEMWRITE, 0, 0, HEADERLEN],
[I_MEMWRITE, 0, 1, S_NORMAL],
[I_MEMWRITE, 0, 2, 0],
[I_MEMWRITE, 0, 3, 100],
[I_MEMWRITE, 0, 4, 100],
[I_MEMWRITE, 0, 5, 0],#ip
[I_MEMWRITE, 0, 6, 0],#cap
[I_MEMWRITE, 0, 7, 2],#code
[I_MEMWRITE, 0, 8, 1],
[I_MEMWRITE, 0, 9, I_MEMCREATE],
[I_MEMWRITE, 0, 10, 1+ARGLEN[I_ALLOC]],
[I_MEMWRITE, 0, 11, I_ALLOC],
[I_MEMWRITE, 0, 12, 0],
[I_MEMWRITE, 0, 13, 15],
[I_MEMWRITE, 0, 14, 0],#data

[I_CREATE, 0],
[I_TRANSFERCAP, 1, 0],


[I_RECURSE, 1, 100, 100],
[I_ALLOC, 0, 10],
]

startcode = str(code)
world = run(code)
#print(code)
#print(SNAMES[world[0][0][0]])
visualize(world, startcode)
