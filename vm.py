from instructions import *
from representations import validate

def run(code, gas, mem):
	"""Create a new process with code and run it with gas and memory resource restrictions"""

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

	STEP = 0
	while True:
		#print(STEP, [world[node][HEADER][H_GAS] for node in chain])
		STEP += 1

		if len(chain) == 0:
			#print("END")
			return world
			#break

		while True:
			current = chain[-1]
			rec = world[current][HEADER][H_REC]
			if rec != current:
				chain.append(rec)
			else:
				break

		print(chain)

		this = world[chain[-1]]

		#if not validate(this):
			#jump_back(S_OOF)
			#continue
		#	os._exit(1)

		header = this[HEADER]
		keys = this[KEYS]
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

			if len(chain) > 0:
				world[chain[-1]][HEADER][H_REC] = chain[-1]

		def get_key(index):
			return keys[index]

		def set_key(target):
			keys.append(target)

		def has_key(target):
			#return target in keys
			return target < len(keys)

		ip = header[H_IP]
		if ip >= len(code):
			print("lencode")
			jump_back(S_OOC)
			continue

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

		args = C[1:]

		IMMEDIATE = {
			I_PUSH: 1
		}

		if (I not in IMMEDIATE and len(args) != 0) or (I in IMMEDIATE and len(args) != IMMEDIATE[I]):
			print("arglen")
			jump_back(S_OOA)
			continue

		req = REQUIREMENTS[I]

		if len(stack) < req[R_ARG]:
			print("ARGLEN", "Stacklen:", len(this[STACK]), "Arglen:", req[R_ARG], INAMES[I])
			jump_back(S_OOS)
			continue

		gascost = req[R_GAS]
		if gascost is None:
			gascost = stack[-1]#size arg for ALLOC

		memcost = req[R_MEM]
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
			"""Push a word on the stack"""
			this[STACK].append(x)

		def peek():
			"""Retrieve (but do not pop) the topmost word of the stack
			Depends on checking ARGLEN correctly"""
			return this[STACK][-1]

		def pop(n=1):
			"""Pop the <n> topmost words from the stack"""
			args = [stack.pop(-1) for i in range(n)]
			return args[::-1]

		def pop1():
			"""Pop the topmost word from the stack"""
			return stack.pop(-1)

		# TODO derive docs from scanning functions?

		if I == I_CREATE:
			"""Create a new process from the given <memory>"""
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
			newproc[KEYS] = []#TODO it's own call key! (?)
			#print("NEW", newproc)
			world.append(newproc)

			set_key(index)
			this[STACK].append(index)

		elif I == I_ALLOC:
			"""Allocate <size> words at the end of <memory>"""
			memory, size = pop(2)
			try:
				this[DATA][memory] += [0 for i in range(size)]
			except IndexError:
				#TODO other code
				print("index")
				jump_back(S_OOA, node_index-1)
				continue

		elif I == I_TRANSFERKEY:
			"""Transfer the key <transferkeyindex> to the process pointed to by <targetkeyindex>
			Should probably be renamed, because it rather "copies" the key"""
			targetkeyindex, transferkeyindex = pop(2)

			if has_key(targetkeyindex) and has_key(transferkeyindex):
				world[this[KEYS][targetkeyindex]][KEYS].append(this[KEYS][transferkeyindex])

		elif I == I_RECURSE:
			"""Recurse into process pointed to by <keyindex>, with <gas> and <mem> limits"""
			keyindex, gas, mem = pop(3)

			if has_key(keyindex):

				target = this[KEYS][keyindex]

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
			"""Push the number of memories onto the stack"""
			try:
				push(len(this[DATA]))#must be serialized!
			except IndexError:
				jump_back(S_OOA)
				#print("memsize")
				continue

		elif I == I_MEMWRITE:
			"""Write <data> to the <memory> at <address>"""
			memory, address, data = pop(3)
			try:
				this[DATA][memory][address] = data
			except IndexError:
				#print("memwrite")
				jump_back(S_OOA)
				continue

		elif I == I_MEMCREATE:
			"""Create a new empty memory"""
			this[DATA].append([])

		elif I == I_ADD:
			"""Compute <arg1> + <arg2> and push the result on the stack"""
			arg1, arg2 = pop(2)
			push((arg1 + arg2) % WORDSIZE)

		elif I == I_SUB:
			"""Compute <arg1> - <arg2> and push the result on the stack"""
			arg1, arg2 = pop(2)
			push((arg1 - arg2) % WORDSIZE)

		elif I == I_MUL:
			"""Compute <arg1> * <arg2> and push the result on the stack"""
			arg1, arg2 = pop(2)
			push((arg1 * arg2) % WORDSIZE)

		elif I == I_DIV:
			"""Compute <arg1> / <arg2> and push the result on the stack"""
			arg1, arg2 = pop(2)
			push((arg1 // arg2) % WORDSIZE)

		elif I == I_JUMP:
			"""Set the instruction pointer to <target> (unconditional jump/goto)"""
			target = pop1()
			this[HEADER][H_IP] = target
			JUMP = True

		elif I == I_JUMPIF:
			"""Set the instruction pointer to <target> if <condition> > 0 (conditional jump)"""
			condition, target = pop(2)
			if condition > 0:
				this[HEADER][H_IP] = target
				JUMP = True

		elif I == I_CODEREAD:
			"""Push the <code_index> word of the own flattened representation onto the stack"""
			code_index = pop(1)
			push(flat(this)[code_index])
			#flatten(this[CODE])[code_index]

		elif I == I_CODELEN:
			"""Push the length of the own flattened representation onto the stack"""
			push(len(flat(this)))#len(flatten(this[CODE]))

		elif I == I_PUSH:
			"""Pushes the immediate argument onto the stack"""
			push(args[0])

		elif I == I_DUP:
			"""Duplicate the topmost element of the stack"""
			push(peek())

		elif I == I_MEMPUSH:
			"""Depending on <memory>, read either from (0:HEADER, 1:CODE, 2: n-2 memory) at <address>"""
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
			"""Duplicate this process and receive its key"""
			#memory = pop1()
			index = len(world)

			from copy import deepcopy
			newproc = deepcopy(this)

			newproc[HEADER] = [S_NORMAL, len(world), 0, 0, 0]
			newproc[KEYS] = []#TODO it's own call key! (?)
			#print("NEW", newproc)
			world.append(newproc)

			set_key(index)
			this[STACK].append(len(this[KEYS])-1)

		elif I == I_HALT:
			"""Set the halt status on this process and jump back to parent."""
			jump_back(S_HLT)
			continue

		elif I == I_RETURN:
			"""Set the return status on this process and jump back to parentself.
			Used to indicate that return values are available (TODO)"""
			jump_back(S_RET)
			continue

		elif I == I_RANDOM:
			"""(Temporary) random number generator: integer between <mi> and <ma> (exclusive)"""
			mi, ma = pop(2)
			from random import randint
			push(randint(mi, ma))

		elif I == I_NUMKEYS:
			"""Push the number of owned keys on the stack"""
			push(len(this[KEYS]))


		if not JUMP:
			header[H_IP] += 1
