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

	return [len(s[HEADER])] + s[HEADER] + caps + [len(s[CODE])] + code + [len(s[DATA])] + data + [len(s[STACK])] + s[STACK]

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
	firstlevel = isinstance(sharp, list) and isinstance(sharp[HEADER], list) and isinstance(sharp[CAPS], list)
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

def run(code, gas, mem):
	#TODO: make CAPS dict? other data structure?
	process = [[S_NORMAL,0,gas,mem,0], [0], code, [], []]

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
		#print(STEP, [world[node][HEADER][H_GAS] for node in chain])
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

		# use raise here?
		def jump_back(condition, to=None):
			nonlocal chain, JB
			JB = True
			header[H_STATUS] = condition
			# TODO make this nicer
			if to is None:
				#world[active] = flat(world[active])
				chain = chain[:-1]
			else:
				chain = chain[:to+1]

		def get_cap(index):
			return caps[index]

		def set_cap(target):
			caps.append(target)

		def has_cap(target):
			#return target in caps
			return target < len(caps)

		ip = header[H_IP]
		if ip >= len(code):#could also wrap around for shits and giggles
			print("lencode")
			jump_back(S_OOC)
			continue

		#print(ip, len(code))
		try:
			C = code[ip]
			I = C[0]
		except IndexError:
			print("ipindex")
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
			jump_back(S_OOA)
			continue
		#print("STACK", this[STACK])
		if len(stack) < ARGLEN[I]:
			print("ARGLEN", "Stacklen:", len(this[STACK]), "Arglen:", ARGLEN[I], INAMES[I])
			jump_back(S_OOS)
			continue

		gascost = IGASCOSTS[I]
		if gascost is None:
			gascost = stack[-1]#size arg for ALLOC

		memcost = IMEMCOSTS[I]
		if memcost is None:
			if I == I_ALLOC:
				memcost = stack[-1]#size arg for ALLOC
			elif I == I_TRANSFERKEY:
				memcost = 1

		for node_index, node in enumerate(chain):
			node_header = world[node][HEADER]
			if not validate(world[node]):
				#TODO this is too heavy
				print("noval")
				jump_back(S_OOF, node_index-1)
				continue
			if node_header[H_GAS] < gascost:
				jump_back(S_OOG, node_index-1)
				continue
			if node_header[H_MEM] < memcost:
				jump_back(S_OOM, node_index-1)
				continue


		if JB:
			continue

		# First check all conditions, then change the state!
		for node_index, node in enumerate(chain):
			world[node][HEADER][H_GAS] -= gascost
			world[node][HEADER][H_MEM] -= memcost

		#debug()
		print(len(chain), "> STEP", STEP, "#%s" % header[H_IP], INAMES[I], args[0] if args else "None", this[STACK])#, this[DATA])

		JUMP = False

		def push(x):
			this[STACK].append(x)

		def peek():
			"""Depends on checking ARGLEN correctly"""
			return this[STACK][-1]

		def pop(n=1):
			args = [stack.pop(-1) for i in range(n)]
			return args[::-1]

		def pop1():
			return stack.pop(-1)

		# TODO derive docs from scanning functions?

		if I == I_CREATE:
			memory = pop1()
			index = len(world)

			#try:
			#	print(len(this[DATA]), memory)
			#	print(this[DATA][memory])
			#print(this[DATA][memory])
			newproc = sharp(this[DATA][memory])
			#except IndexError as e:
				#TODO set STATUS
			#	print("FAILCREATE", e)
			#	jump_back(S_OOF)
			#	continue
			newproc[HEADER] = [S_NORMAL, 0, 0, 0, 0]
			newproc[CAPS] = []#TODO it's own call cap! (?)
			#print("NEW", newproc)
			world.append(newproc)

			set_cap(index)
			this[STACK].append(index)

		elif I == I_ALLOC:
			memory, size = pop(2)
			try:
				this[DATA][memory] += [0 for i in range(size)]
			except IndexError:
				#TODO other code
				print("index")
				jump_back(S_OOA, node_index-1)
				continue

		elif I == I_TRANSFERKEY:
			"""Should probably be renamed, because it rather "copies" the key"""
			# TODO can only transfer 1 cap per call
			# only relative indices?
			# how do you say "do you have cap for x" otherwise?
			targetcapindex, transfercapindex = pop(2)

			if has_cap(targetcapindex) and has_cap(transfercapindex):
				world[this[CAPS][targetcapindex]][CAPS].append(this[CAPS][transfercapindex])

		elif I == I_RECURSE:
			capindex, gas, mem = pop(3)

			if has_cap(capindex):

				target = this[CAPS][capindex]

				target_header = world[target][HEADER]
				target_header[H_GAS] = min(header[H_GAS], gas)
				target_header[H_MEM] = min(header[H_MEM], mem)

				header[H_REC] = target
				header[H_STATUS] = S_REC
				#active = target
				# TODO recurse down if subprocess has S/H_REC, because refuel?
				# or further up?
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
			arg1, arg2 = pop(2)
			push((arg1 + arg2) % WORDSIZE)

		elif I == I_SUB:
			arg1, arg2 = pop(2)
			push((arg1 - arg2) % WORDSIZE)

		elif I == I_MUL:
			arg1, arg2 = pop(2)
			push((arg1 * arg2) % WORDSIZE)

		elif I == I_DIV:
			arg1, arg2 = pop(2)
			push((arg1 // arg2) % WORDSIZE)

		elif I == I_JUMP:
			target = pop1()
			this[HEADER][H_IP] = target
			JUMP = True

		elif I == I_JUMPIF:
			condition, target = pop(2)
			if condition > 0:
				this[HEADER][H_IP] = target
				JUMP = True

		elif I == I_CODEREAD:
			code_index = pop(1)
			push(flat(this)[code_index])
			#flatten(this[CODE])[code_index]

		elif I == I_CODELEN:
			push(len(flat(this)))#len(flatten(this[CODE]))

		elif I == I_PUSH:
			push(args[0])

		elif I == I_DUP:
			push(peek())

		elif I == I_MEMPUSH:
			memory, address = pop(2)
			try:

				if memory == 0:
					push(this[HEADER][address])
				elif memory == 1:
					push(this[CODE][address])
				else:
					push(this[DATA][memory-2][address])#len(flatten(this[CODE]))
			except IndexError:
				jump_back(S_OOB)
				continue
		elif I == I_FORK:
			#memory = pop1()
			index = len(world)

			from copy import deepcopy
			newproc = deepcopy(this)

			newproc[HEADER] = [S_NORMAL, len(world), 0, 0, 0]
			newproc[CAPS] = []#TODO it's own call cap! (?)
			#print("NEW", newproc)
			world.append(newproc)

			set_cap(index)
			this[STACK].append(len(this[CAPS])-1)

		elif I == I_HALT:
			jump_back(S_HLT)
			continue

		elif I == I_RETURN:
			jump_back(S_RET)
			continue

		elif I == I_RANDOM:
			mi, ma = pop(2)
			from random import randint
			push(randint(mi, ma))

		elif I == I_NUMCAPS:
			push(len(this[CAPS]))


		if not JUMP:
			header[H_IP] += 1
