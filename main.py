#NAND machine?


HEADER, CAPS, CODE, DATA = range(4)

# Add status flag for non-terminating failures?
HEADERLEN = 5
H_STATUS, H_REC, H_GAS, H_MEM, H_IP = range(HEADERLEN)

STATUSLEN = 6
S_NORMAL, S_OOC, S_OOG, S_OOM, S_OOA, S_OOF = range(STATUSLEN)

NUMINSTR = 7
I_CREATE, I_ALLOC, I_TRANSFERCAP, I_RECURSE, I_MEMSIZE, I_MEMWRITE, I_MEMCREATE = range(NUMINSTR)

INAMES = "I_CREATE, I_ALLOC, I_TRANSFERCAP, I_RECURSE, I_MEMSIZE, I_MEMWRITE, I_MEMCREATE".split(", ")

ARGLEN = {
	I_CREATE: 1,
	I_ALLOC: 2,
	I_TRANSFERCAP: 2,
	I_RECURSE: 3,
	I_MEMSIZE: 1,
	I_MEMWRITE: 3,
	I_MEMCREATE: 0,
}

IGASCOSTS = {
	I_CREATE: HEADERLEN,
	I_ALLOC: None,
	I_TRANSFERCAP: 6,
	I_RECURSE: 20,
	I_MEMSIZE: 1,
	I_MEMWRITE: 2,
	I_MEMCREATE: 4,
}

IMEMCOSTS = {
	I_CREATE : HEADERLEN,#plus some constant overhead for lists?
	I_ALLOC: None,
	I_TRANSFERCAP: None,
	I_RECURSE: 0,
	I_MEMSIZE: 0,
	I_MEMWRITE: 0,
	I_MEMCREATE: 2,
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
	print(f)
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
	secondlevel = all([isinstance(instr, list) and all([isinstance(i, int) for i in instr]) for instr in sharp[2]])
	if not secondlevel:
		return False
	return True

def run(code):
	#TODO: make CAPS dict? other data structure?
	process = [[S_NORMAL,0,1000,1000,0], {0}, code, []]
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

	print("CHAIN", chain)
	#traverse H_REC here?

	STEP = 0
	while True:
		STEP += 1

		# TODO add jump-back logic to last process in parent chain that has sufficient resources

		if len(chain) == 0:
			print("END")
			return world
			#break
		this = world[chain[-1]]

		if not validate(this):
			#jump_back(S_OOF)
			#continue
			os._exit(1)

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
			jump_back(S_OOA)#TODO maybe other code here?
			continue

		#TODO check length
		args = C[1:]

		if len(args) != ARGLEN[I]:
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
			if not validate(node):
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
			newproc[CAPS] = set()
			#print("NEW", newproc)
			world.append(newproc)

			set_cap(index)

		elif I == I_ALLOC:
			memory, size = args
			try:
				this[DATA][memory] += [0 for i in range(size)]
			except IndexError:
				#TODO other code
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

		elif I == I_MEMWRITE:
			memory, address, data = args
			try:
				this[DATA][memory][address] = data
			except IndexError:
				jump_back(S_OOA)

		elif I == I_MEMCREATE:
			this[DATA].append([])

#H_STATUS, H_REC, H_GAS, H_MEM, H_IP
code = [
[I_MEMCREATE],
[I_ALLOC, 0, 10],
[I_MEMWRITE, 0, 0, HEADERLEN],
[I_MEMWRITE, 0, 1, 0],
[I_MEMWRITE, 0, 2, 0],
[I_MEMWRITE, 0, 3, 100],
[I_MEMWRITE, 0, 4, 100],
[I_MEMWRITE, 0, 5, 0],
[I_MEMWRITE, 0, 6, 1],
[I_MEMWRITE, 0, 7, 1],
[I_MEMWRITE, 0, 8, 0],
[I_MEMWRITE, 0, 9, 0],
[I_CREATE, 0],
[I_TRANSFERCAP, 1, 0],
[I_RECURSE, 1, 100, 100],
[I_ALLOC, 0, 10],
]

import json
import os
import sys

from time import time


from graphviz import Digraph

def visualize(world, startcode):

	dot = Digraph()
	dot.format = "svg"

	def name(index):
		return "%i [%i|%i]" % (index, world[index][HEADER][H_GAS], world[index][HEADER][H_MEM])

	#TODO highlight active
	if not isinstance(world[0][0], list):
		print("VIZ NOT SHARP")
		return

	edges = 0
	for pi, proc in enumerate(world):
		for cap in proc[CAPS]:
			edges += 1
			dot.edge(name(pi), name(cap), color="black")

	if edges > 3:
		fname = str(int(time()*10000))
		with open("graphs/"+fname+".txt", "w+") as f:
			f.write(startcode)
		dot.render("graphs/"+fname)#, view=True)




def main():
	try:
		data = sys.stdin.read()
		code = json.loads(data)
	except (UnicodeError, json.decoder.JSONDecodeError):
		os._exit(0)

	world = run(code)
	visualize(world, data)
	os._exit(0)

if __name__ == "__main__":
	import afl
	afl.start()
	main()
