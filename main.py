#NAND machine?


HEADER, CAPS, CODE, DATA = range(4)

HEADERLEN = 4
H_REC, H_GAS, H_MEM, H_IP = range(HEADERLEN)

CAPW, CAPR, CAPC = range(3)

I_CREATE, I_ALLOC, I_RECURSE, I_MEMSIZE, I_NANDI, I_NAND = range(6)

IGASCOSTS = {
	I_CREATE: HEADERLEN,
	I_ALLOC: None,
	I_RECURSE: 4,
	I_MEMSIZE: 1,
	I_NANDI: 2,
	I_NAND: 3
}

IMEMCOSTS = {
	I_CREATE : HEADERLEN,#plus some constant overhead for lists?
	I_ALLOC: None,
	I_RECURSE: 0,
	I_MEMSIZE: 0,
	I_NANDI: 0,
	I_NAND: 0
}

#allow for reduction of caps?

# does it always jump back to the minimum of all header resources?

#def decode():
#def start()

code = [
[I_CREATE],
[I_ALLOC, 1, 4],
[I_RECURSE, 1, 100, 100, 0, 0, 1]
]

def pretty(p):
	h = p[HEADER]
	c = p[CAPS]
	numbers = [str(h[i]) for i in [H_REC, H_GAS, H_MEM, H_IP]]
	caps = [str(c[i]) for i in [CAPW, CAPR, CAPC]]
	head = "\t".join(numbers+caps)

	body = str(p[DATA])# str(p[CODE]) +
	return head + "\n" + body

#TODO: make CAPS dict? other data structure?
process = [[0,1000,1000,0], [{0},{0},{0}], code, []]
world = [process]

active = 0
#traverse H_REC here?

STEP = 0

while True:
	STEP += 1

	this = world[active]

	#TODO: only deserialize here, on demand

	header = this[HEADER]
	caps = this[CAPS]
	code = this[CODE]

	def set_cap(type, target):
		caps[type].add(target)

	def has_cap(type, target):
		return target in caps[type]

	def can_call(target):
		return has_cap(CAPC, target)

	def can_write(target):
		return has_cap(CAPW, target)

	def can_read(source):
		return has_cap(CAPR, target)

	ip = header[H_IP]
	if ip >= len(code):#could also wrap around for shits and giggles
		print("OOC JUMP", active)
		break

	C = code[ip]
	I = C[0]
	#TODO check length
	args = C[1:]

	gascost = IGASCOSTS[I]
	if gascost is None:
		gascost = args[1]#size arg for ALLOC

	if header[H_GAS] < gascost:
		print("OOG JUMP")
		break

	header[H_GAS] -= gascost

	memcost = IMEMCOSTS[I]
	if memcost is None:
		memcost = args[1]#size arg for ALLOC

	if header[H_MEM] < memcost:
		print("OOM JUMP")
		break

	header[H_MEM] -= memcost

	print("\nSTEP#"	 + str(STEP), I)
	for proc in world:
		print(pretty(proc))

	header[H_IP] += 1

	def transfer_cap(type, index, table):
		if index in caps[type]:
			table[type].add(index)

	if I == I_CREATE:
		index = len(world)
		if index >= 64:
			raise Exception("FUCK")

		world.append([[0, 0, 0, 0], [{index},{index},{index}], [], []])#FLAT: newheader()+[]+[])#

		set_cap(CAPW, index)
		set_cap(CAPR, index)
		set_cap(CAPC, index)

		# created cap can't read or write to self yet! should this really depend on index? always allow self-access? for now, yes

	elif I == I_ALLOC:
		target, size = args
		if can_write(target):
			world[target][DATA] += [0 for i in range(size)]

	elif I == I_RECURSE:
		target, gas, mem, wcap, rcap, ccap = args

		if can_call(target):
			target_caps = world[target][CAPS]

			# TODO can only transfer 1 cap per call
			transfer_cap(CAPW, wcap, target_caps)
			transfer_cap(CAPR, rcap, target_caps)
			transfer_cap(CAPC, ccap, target_caps)

			target_header = world[target][HEADER]
			target_header[H_GAS] = min(header[H_GAS], gas)
			target_header[H_MEM] = min(header[H_MEM], mem)

			header[H_REC] = target
			active = target

	elif I == I_MEMSIZE:
		target, target_index, source = args
		if can_write(target) and can_read(source):
			world[target][DATA][target_index] = len(world[source])#must be serialized!

	elif I == I_NANDI:
		#communicate over third domain?
		target, target_index, data = args
		if can_write(target) and can_read(target):
			# if target isn't flat, can't write code
			world[target][DATA][target_index] = ~(data & world[target][DATA][target_index])

	elif I == I_NAND:
		target, target_index, source, source_index = args
		if can_write(target) and can_read(source):
			world[target][DATA][target_index] = ~(data & world[source][DATA][source_index])

from graphviz import Digraph



def visualize():

	dot = Digraph()
	dot.format = "svg"

	for pi, proc in enumerate(world):
		for type in [CAPW, CAPR, CAPC]:
			for cap in proc[CAPS][type]:
				print(pi, cap)
				dot.edge(str(pi), str(cap), color=["red", "green", "blue"][type])

	dot.render("graph", view=True)

visualize()
