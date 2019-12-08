from assembler import asm
from vm import run_from_code
from visualize import visualize

code = """
memcreate
alloc(0,2)
memwrite(0,0,fork())
memwrite(0,1,fork())
transferkey(1, random(0, numkeys()))
transferkey(2, random(0, numkeys()))
recurse(mempush(2,0), div(mempush(0,2), 3), div(mempush(0,3), 3))
recurse(mempush(2,1), div(mempush(0,2), 2), div(mempush(0,3), 2))
"""

if __name__ == "__main__":
	binary = asm(code)
	startcode = str(binary)

	world = run_from_code(binary, 10000, 10000)

	visualize(world, startcode)
