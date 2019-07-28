WORDSIZE = 2**16
WORDMASK = WORDSIZE-1

HEADER, CAPS, CODE, DATA, STACK = range(5)

# Add status flag for non-terminating failures?
HEADERLEN = 5
H_STATUS, H_REC, H_GAS, H_MEM, H_IP = range(HEADERLEN)

STATUSLEN = 11
# difference between oos and ooa?
# Should S_REC exist? Can see in H_REC if there is subprocess
S_NORMAL, S_REC, S_HLT, S_RET, S_OOC, S_OOG, S_OOM, S_OOA, S_OOF, S_OOS, S_OOB = range(STATUSLEN)
SNAMES = "S_NORMAL, S_REC, S_HLT, S_RET, S_OOC, S_OOG, S_OOM, S_OOA, S_OOF, S_OOS, S_OOB".split(", ")
#normal, halt, return, out of code, out of gas, out of memory, out of arguments, out of form?, out of stack, out of bounds

NUMINSTR = 20
I_HALT, I_RETURN, I_CREATE, I_ALLOC, I_TRANSFERKEY, I_RECURSE, I_MEMSIZE, I_MEMWRITE, I_MEMCREATE, I_ADD, I_SUB, I_MUL, I_DIV, I_JUMP, I_JUMPIF, I_CODEREAD, I_CODELEN, I_PUSH, I_MEMPUSH, I_FORK = range(NUMINSTR)
INAMES = "I_HALT, I_RETURN, I_CREATE, I_ALLOC, I_TRANSFERKEY, I_RECURSE, I_MEMSIZE, I_MEMWRITE, I_MEMCREATE, I_ADD, I_SUB, I_MUL, I_DIV, I_JUMP, I_JUMPIF, I_CODEREAD, I_CODELEN, I_PUSH, I_MEMPUSH, I_FORK".split(", ")

#On Stack
ARGLEN = {
	I_HALT: 0,
	I_RETURN: 0,
	I_CREATE: 1,
	I_ALLOC: 2,
	I_TRANSFERKEY: 2,
	I_RECURSE: 3,
	I_MEMSIZE: 1,
	I_MEMWRITE: 3,
	I_MEMCREATE: 0,
	I_ADD: 2,
	I_SUB: 2,
	I_MUL: 2,
	I_DIV: 2,
	I_JUMP: 1,
	I_JUMPIF: 2,
	I_CODEREAD: 1,
	I_CODELEN: 0,
	I_PUSH: 0,
	I_MEMPUSH: 2,
	I_FORK: 0,
}

IGASCOSTS = {
	I_HALT: 1,
	I_RETURN: 1,
	I_CREATE: HEADERLEN,
	I_ALLOC: None,
	I_TRANSFERKEY: 6,
	I_RECURSE: 20,
	I_MEMSIZE: 1,
	I_MEMWRITE: 2,
	I_MEMCREATE: 4,
	I_ADD: 5,
	I_SUB: 5,
	I_MUL: 10,
	I_DIV: 20,
	I_JUMP: 2,
	I_JUMPIF: 5,
	I_CODEREAD: 8,
	I_CODELEN: 3,#TODO: mind flatten()
	I_PUSH: 2,
	I_MEMPUSH: 4,
	I_FORK: 40,
}

# TODO: cost -= arglen
IMEMCOSTS = {
	I_HALT: 0,
	I_RETURN: 0,
	I_CREATE : HEADERLEN,#plus some constant overhead for lists?
	I_ALLOC: None,
	I_TRANSFERKEY: None,
	I_RECURSE: 0,
	I_MEMSIZE: 0,
	I_MEMWRITE: 0,
	I_MEMCREATE: 2,
	I_ADD: -1,
	I_SUB: -1,
	I_MUL: -1,
	I_DIV: -1,
	I_JUMP: 0,
	I_JUMPIF: 0,
	I_CODEREAD: 0,
	I_CODELEN: 0,
	I_PUSH: 1,
	I_MEMPUSH: 0,
	I_FORK: 0,#TODO
}
