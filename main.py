from assembler import asm
from vm import run
from visualize import visualize


#codelen(0,0)
code = """
memcreate
alloc(0,2)
memwrite(0,0,fork())
memwrite(0,1,fork())
transferkey(1, random(0, numcaps()))
transferkey(2, random(0, numcaps()))
recurse(mempush(2,0), div(mempush(0,2), 3), div(mempush(0,3), 3))
recurse(mempush(2,1), div(mempush(0,2), 2), div(mempush(0,3), 2))
"""

binary = asm(code)
#print(binary)
#print("LEN", len(binary))

if __name__ == "__main__":
	startcode = str(binary)
	world = run(binary, 10000, 10000)
	#print(code)
	#print(world)
	#print(SNAMES[world[0][0][0]])
	visualize(world, startcode)
