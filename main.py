"""
only metering relation is hierarchical, processes are created in the same space - but can't call each other? how will that work
reify access via capabilities - but cap system should be implemented within, not on the substrate
can only call parent meter?
or DO provide simple cap system? what else other than access is needed?
RECURSE instruction has memory cost! (say, 3 words for overhead->index,gas,mem)
but only if theres metadata that isnt contained in process snapshot, which there isn't!
ideally, not only memory requirements of process image, but runtime representation as well, if its worse
vm implemented in itself, then measure?

creator gets cap: which is index!
so RECURSE gets cap argument!!!
the (only) problem i see here is the non-fixed-size header which makes this a bit awkward
UNLESS
it's a bit field!
then every process could have, say 64 caps/references
ah, keykos had capability to capability table
ah, i see, a fixed limit kind of, but not really limits the number of subprocs a process can create in sequence, without passing down other caps

read vs write caps

flat vs hierarchy
not sure what advantages of hierarchy are
"""

#NAND machine?

# HEADER: status?, gas, mem, bitmap, ip
H_REC, H_GAS, H_MEM, H_CAPW, H_CAPR, H_CAPC, H_IP = range(5)

def newheader():
	header = [0, 0, 0, 0x00, 0x00, 0]

HEADER, CODE, DATA = range(3)

I_CREATE, I_ALLOC, I_RECURSE, I_NANDI, I_NAND = range(3)

IMEMCOSTS = {
	I_CREATE : len(newheader()),#plus some constant overhead for lists?
	I_ALLOC: None,
	I_RECURSE: 0,
	I_NANDI: 0,
	I_NAND: 0
}

#allow for reduction of caps?


this = world[this]
header = this[HEADER]
code = this[CODE]

def can_call(target):
	return (header[H_CAPC] >> target) & 0x1 == 1

def can_write(target):
	return (header[H_CAPW] >> target) & 0x1 == 1

def can_read(source):
	return (header[H_CAPR] >> source) & 0x1 == 1

I = code[header[H_IP]]

if I_CREATE:
	index = len(world)
	if index >= 64:
		raise "FUCK"
		
	world.append([newheader(), []])
	header[H_CAPC] |= 1<<index
	header[H_CAPW] |= 1<<index
	header[H_CAPR] |= 1<<index

elif I_ALLOC:
	target, size = args[-2:]
	if can_write(target):
		world[target][DATA].append([0 for i in range(size)])
	
elif I == I_RECURSE:
	target, cmask, wmask, rmask, gas, mem = args[:-6]
	
	if can_call(target):
		target_header = world[target][HEADER]	
		target_header[H_CAPW] |= header[H_CAPW] & wmask
		target_header[H_CAPR] |= header[H_CAPR] & rmask
		target_header[H_CAPC] |= header[H_CAPC] & cmask
		
		target_header[H_GAS] = min(header[H_GAS], gas)
		target_header[H_MEM] = min(header[H_MEM], mem)
		
		header[H_REC] = target

elif I == I_NANDI:
	#communicate over third domain?
	target, target_index, data = args[-3:]
	if can_write(target):
		world[target][DATA][target_index] ~&= data
		
elif I == I_NAND:
	target, target_index, source, source_index
	if can_write(target) and can_read(source):
		world[target][DATA][target_index] ~&= world[source][DATA][source_index]
