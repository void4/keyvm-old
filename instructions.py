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

NUMINSTR = 23
I_HALT, I_RETURN, I_CREATE, I_ALLOC, I_TRANSFERKEY, I_RECURSE, I_MEMSIZE, I_MEMWRITE, I_MEMCREATE, I_ADD, I_SUB, I_MUL, I_DIV, I_JUMP, I_JUMPIF, I_CODEREAD, I_CODELEN, I_PUSH, I_DUP, I_MEMPUSH, I_FORK, I_RANDOM, I_NUMCAPS = range(NUMINSTR)
INAMES = "I_HALT, I_RETURN, I_CREATE, I_ALLOC, I_TRANSFERKEY, I_RECURSE, I_MEMSIZE, I_MEMWRITE, I_MEMCREATE, I_ADD, I_SUB, I_MUL, I_DIV, I_JUMP, I_JUMPIF, I_CODEREAD, I_CODELEN, I_PUSH, I_DUP, I_MEMPUSH, I_FORK, I_RANDOM, I_NUMCAPS".split(", ")

NUMREQ = 3
R_ARG, R_GAS, R_MEM = range(NUMREQ)

#On Stack
REQUIREMENTS = {
	I_HALT: (0,1,0),
	I_RETURN: (0,1,0),
	I_CREATE: (1,HEADERLEN,HEADERLEN),
	I_ALLOC: (2,None,None),
	I_TRANSFERKEY: (2,6,2),# TODO MEM COST ???
	I_RECURSE: (3,20,0),
	I_MEMSIZE: (1,1,0),
	I_MEMWRITE: (3,2,-1),
	I_MEMCREATE: (0,4,2),
	I_ADD: (2,5,-1),
	I_SUB: (2,5,-1),
	I_MUL: (2,10,-1),
	I_DIV: (2,20,-1),
	I_JUMP: (1,2,0),
	I_JUMPIF: (2,5,0),
	I_CODEREAD: (1,8,0),
	I_CODELEN: (0,3,0),
	I_PUSH: (0,2,1),
	I_DUP: (0,1,1),
	I_MEMPUSH: (2,4,0),
	I_FORK: (0,40,0),#TODO Gas, MEM
	I_RANDOM: (2,2,-1),
	I_NUMCAPS: (0,1,-1),
}

# TODO Temporary
for k,v in REQUIREMENTS.items():
	REQUIREMENTS[k] = (v[0],1,1)
