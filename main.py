#NAND machine?

def flatten(listoflists):
	return sum(listoflists, [])

from instructions import *

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

	return [len(s[HEADER])] + s[HEADER] + caps + [len(s[CODE])] + code + [len(s[DATA])] + data + [len(s[STACK])] + stack

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

	l = read()
	stack = [read() for i in range(l)]

	s = [header, caps, code, data, stack]
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
	firstlevel = isinstance(sharp, list) and isinstance(sharp[HEADER], list) and isinstance(sharp[CAPS], set)
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

def run(code):
	#TODO: make CAPS dict? other data structure?
	process = [[S_NORMAL,0,1000,1000,0], {0}, code, [], []]

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
		stack = this[STACK]

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

		IMMEDIATE = {
			I_PUSH: 1
		}

		if (I not in IMMEDIATE and len(args) != 0) or (I in IMMEDIATE and len(args) != IMMEDIATE[I]):
			print("arglen")
			jump_back(S_OOA, len(chain)-2)
			continue

		if len(stack) < ARGLEN[I]:
			print(len(stack), ARGLEN[I], INAMES[I])
			jump_back(S_OOS)
			continue

		gascost = IGASCOSTS[I]
		if gascost is None:
			gascost = stack[-1]#size arg for ALLOC

		memcost = IMEMCOSTS[I]
		if memcost is None:
			if I == I_ALLOC:
				memcost = stack[-1]#size arg for ALLOC
			elif I == I_TRANSFERCAP:
				memcost = 1

		for node_index, node in enumerate(chain):
			node_header = world[node][HEADER]
			if not validate(world[node]):
				#TODO this is too heavy
				print("noval")
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

		def pop(n=1):
			args = [stack.pop(-1) for i in range(n)]
			return args[::-1]

		def pop1():
			return stack.pop(-1)

		if I == I_CREATE:
			memory = pop1()
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
			memory, size = pop(2)
			try:
				this[DATA][memory] += [0 for i in range(size)]
			except IndexError:
				#TODO other code
				#print("index")
				jump_back(S_OOA, node_index-1)
				continue

		elif I == I_TRANSFERCAP:
			# TODO can only transfer 1 cap per call
			target, cap = pop(2)

			if has_cap(target):
				target_caps = world[target][CAPS]
				transfer_cap(cap, target_caps)

		elif I == I_RECURSE:
			target, gas, mem = pop(3)

			if has_cap(target):

				target_header = world[target][HEADER]
				target_header[H_GAS] = min(header[H_GAS], gas)
				target_header[H_MEM] = min(header[H_MEM], mem)

				header[H_REC] = target
				active = target
				chain.append(target)

		elif I == I_MEMSIZE:
			target_index = pop1()
			try:
				this[DATA][target_index] = len(this[DATA])#must be serialized!
			except IndexError:
				jump_back(S_OOA)
				#print("memsize")
				continue

		elif I == I_MEMWRITE:
			memory, address, data = pop(3)
			try:
				this[DATA][memory][address] = data
			except IndexError:
				#print("memwrite")
				jump_back(S_OOA)
				continue

		elif I == I_MEMCREATE:
			this[DATA].append([])

		elif I == I_ADD:
			memory, address1, address2 = pop(3)
			try:
				this[DATA][memory][address1] = (this[DATA][memory][address1]+this[DATA][memory][address2]) % WORDSIZE
			except IndexError:
				jump_back(S_OOA)
				continue

		elif I == I_SUB:
			memory, address1, address2 = pop(3)
			try:
				this[DATA][memory][address1] = (this[DATA][memory][address1]-this[DATA][memory][address2]) % WORDSIZE
			except IndexError:
				jump_back(S_OOA)
				continue

		elif I == I_JUMP:
			target = pop1()
			this[HEADER][H_IP] = target

		elif I == I_JUMPIF:
			target, memory, address = pop(3)
			try:
				if this[DATA][memory][address] > 0:
					this[HEADER][H_IP] = target
			except IndexError:
				jump_back(S_OOF)
				continue

		elif I == I_CODEREAD:
			code_index, memory, address = pop(3)
			try:
				this[DATA][memory][address] = flat(this)[code_index]#flatten(this[CODE])[code_index]
			except IndexError:
				jump_back(S_OOA)
				continue

		elif I == I_CODELEN:
			memory, address = pop(2)
			try:
				this[DATA][memory][address] = len(flat(this))#len(flatten(this[CODE]))
			except IndexError:
				jump_back(S_OOA)
				continue

		elif I == I_PUSH:
			this[STACK].append(args[0])

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
		dot.render("graphs/"+fname, view=False)

from asmutils import asm
from assembler import assemble

treecode = "jump(0)"
print(treecode)
assembler = "\n".join(asm(treecode))
print(assembler)
binary = assemble(assembler)
print(binary)

if __name__ == "__main__":
	startcode = str(binary)
	world = run(binary)
	#print(code)
	print(world)
	print(SNAMES[world[0][0][0]])
	visualize(world, startcode)
