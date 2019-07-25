#NAND machine?


HEADER, CAPS, CODE, DATA = range(4)

# Add status flag for non-terminating failures?
HEADERLEN = 5
H_STATUS, H_REC, H_GAS, H_MEM, H_IP = range(HEADERLEN)

STATUSLEN = 4
S_NORMAL, S_OOC, S_OOG, S_OOM = range(STATUSLEN)

CAPW, CAPR, CAPC = range(3)

I_CREATE, I_ALLOC, I_TRANSFERCAP, I_RECURSE, I_MEMSIZE, I_WRITESUB, I_NANDI, I_NAND = range(8)

INAMES = "I_CREATE, I_ALLOC, I_TRANSFERCAP, I_RECURSE, I_MEMSIZE, I_WRITESUB, I_NANDI, I_NAND".split(", ")

IGASCOSTS = {
	I_CREATE: HEADERLEN,
	I_ALLOC: None,
	I_TRANSFERCAP: 6,
	I_RECURSE: 20,
	I_MEMSIZE: 1,
	I_WRITESUB: 2,
	I_NANDI: 2,
	I_NAND: 3
}

IMEMCOSTS = {
	I_CREATE : HEADERLEN,#plus some constant overhead for lists?
	I_ALLOC: None,
	I_TRANSFERCAP: None,
	I_RECURSE: 0,
	I_MEMSIZE: 0,
	I_WRITESUB: 0,
	I_NANDI: 0,
	I_NAND: 0
}

def flat(s):
	caps = []
	for i in range(len(s[CAPS])):
		caps += [len(s[CAPS][i])] + list(s[CAPS][i])

	code = []
	for instruction in s[CODE]:
		code += [len(instruction)]
		code += instruction

	return [len(s[HEADER])] + s[HEADER] + caps + [len(s[CODE])] + code + [len(s[DATA])] + s[DATA]

def sharp(f):

	index = 0
	def read():
		nonlocal index
		d = f[index]
		index += 1
		return d

	l = read()
	header = [read() for i in range(l)]

	caps = []
	for i in range(3):
		l = read()
		caps.append({read() for j in range(l)})

	l = read()
	code = [[read() for j in range(read())] for i in range(l)]

	l = read()
	data = [read() for i in range(l)]

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
	caps = [str(c[i]) for i in [CAPW, CAPR, CAPC]]
	head = "\t".join(numbers+caps)

	body = str(p[DATA])# str(p[CODE]) +
	return head + "\n" + body

#allow for reduction of caps?

# does it always jump back to the minimum of all header resources?

#def decode():
#def start()

code = [
[I_CREATE],
[I_TRANSFERCAP, 1, None, None, 0],
[I_ALLOC, 1, 1],
[I_WRITESUB, 1, 15, 42],
[I_RECURSE, 1, 100, 100],
]

def ensure_sharp(target):
	if not isinstance(world[target][0], list):
		world[target] = sharp(world[target])

def ensure_flat(target):
	if isinstance(world[target][0], list):
		world[target] = flat(world[target])

def ensure_mutable(target, target_index):
	ensure_flat(target)
	# TODO: in this unoptimized serialization format, 4 reads required!
	t = world[target]
	headerlen = t[0]
	wcaplen = t[1+headerlen]
	rcaplen = t[1+headerlen+1+wcaplen]
	ccaplen = t[1+headerlen+1+wcaplen+1+rcaplen]
	#print("TARGET", target_index, headerlen, wcaplen, rcaplen, ccaplen)
	endofcaps = 1+headerlen+1+wcaplen+1+rcaplen+1+ccaplen
	if target_index < endofcaps:
		raise Exception("IMMUTABLE")

#TODO: make CAPS dict? other data structure?
process = [[S_NORMAL,0,1000,1000,0], [{0},{0},{0}], code, []]
world = [process]

def debug():
	print("\nSTEP#"	 + str(STEP), INAMES[I])
	for proc in world:
		print(pretty(proc))

start = 0
chain = [start]

while True:
	current = chain[-1]
	ensure_sharp(current)
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
		break
	this = world[chain[-1]]

	#TODO: only deserialize here, on demand

	header = this[HEADER]
	caps = this[CAPS]
	code = this[CODE]

	JB = False

	def jump_back(condition, to=None):
		global chain, JB
		JB = True
		header[H_STATUS] = condition
		# TODO make this nicer
		if to is None:
			world[active] = flat(world[active])
			chain = chain[:-1]
		else:
			for i in range(len(world)-1, to, -1):
				world[i] = flat(world[i])
				chain = chain[:-1]

	def set_cap(type, target):
		caps[type].add(target)

	def has_cap(type, target):
		return target in caps[type]

	def transfer_cap(type, index, table):
		#print("TRANSFER", type, index, caps[type])
		if index in caps[type]:
			table[type].add(index)

	def can_call(target):
		return has_cap(CAPC, target)

	def can_write(target):
		return has_cap(CAPW, target)

	def can_read(source):
		return has_cap(CAPR, target)

	ip = header[H_IP]
	if ip >= len(code):#could also wrap around for shits and giggles
		jump_back(S_OOC)
		continue

	print(ip, len(code))
	C = code[ip]
	I = C[0]
	#TODO check length
	args = C[1:]

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

	debug()

	header[H_IP] += 1

	if I == I_CREATE:
		index = len(world)

		newproc = flat([[0, 0, 0, 0, 0], [{index},{index},{index}], [], []])
		#print("NEW", newproc)
		world.append(newproc)

		set_cap(CAPW, index)
		set_cap(CAPR, index)
		set_cap(CAPC, index)

	elif I == I_ALLOC:
		target, size = args
		if can_write(target):
			# TODO this is weird
			world[target] = sharp(world[target])
			world[target][DATA] += [0 for i in range(size)]
			world[target] = flat(world[target])

	elif I == I_TRANSFERCAP:
		target, wcap, rcap, ccap = args

		if can_call(target):
			world[target] = sharp(world[target])

			target_caps = world[target][CAPS]

			# TODO can only transfer 1 cap per call
			transfer_cap(CAPW, wcap, target_caps)
			transfer_cap(CAPR, rcap, target_caps)
			transfer_cap(CAPC, ccap, target_caps)
			world[target] = flat(world[target])

	elif I == I_RECURSE:
		target, gas, mem = args

		if can_call(target):
			world[target] = sharp(world[target])

			target_header = world[target][HEADER]
			target_header[H_GAS] = min(header[H_GAS], gas)
			target_header[H_MEM] = min(header[H_MEM], mem)

			header[H_REC] = target
			active = target

	elif I == I_MEMSIZE:
		target, target_index, source = args
		if can_write(target) and can_read(source):
			world[target][DATA][target_index] = len(world[source])#must be serialized!

	elif I == I_WRITESUB:
		target, target_index, data = args
		if can_write(target):
			ensure_mutable(target, target_index)
			#TODO ensure_flat, ensure not self
			world[target][target_index] = data
			print("WRITING")

	elif I == I_NANDI:
		#communicate over third domain?
		target, target_index, data = args
		if can_write(target) and can_read(target):
			ensure_sharp(target)
			ensure_sharp(source)
			world[target][DATA][target_index] = ~(data & world[target][DATA][target_index])

	elif I == I_NAND:
		target, target_index, source, source_index = args
		if can_write(target) and can_read(source):
			world[target][DATA][target_index] = ~(data & world[source][DATA][source_index])

debug()

from graphviz import Digraph

def visualize():

	dot = Digraph()
	dot.format = "svg"

	def name(index):
		return "%i [%i|%i]" % (index, world[index][HEADER][H_GAS], world[index][HEADER][H_MEM])

	#TODO highlight active

	for pi, proc in enumerate(world):
		for type in [CAPW, CAPR, CAPC]:
			for cap in proc[CAPS][type]:
				dot.edge(name(pi), name(cap), color=["red", "green", "blue"][type])

	dot.render("graph", view=True)

#visualize()
