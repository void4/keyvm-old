from time import time
import os

from graphviz import Digraph

from instructions import *

os.system("mkdir -p graphs")

def visualize(world, startcode):

	dot = Digraph()
	dot.format = "svg"

	def name(index):
		header = world[index][HEADER]
		#return "%i [%s|%i|%i|%s|%s]" % (index, SNAMES[header[H_STATUS]], header[H_GAS], header[H_MEM], str(world[index][CODE]), str(world[index][DATA]))
		return "%i [%s|%i|%i]" % (index, SNAMES[header[H_STATUS]], header[H_GAS], header[H_MEM])


	#TODO highlight active
	if not isinstance(world[0][0], list):
		print("VIZ NOT SHARP")
		return

	edges = 0
	for pi, proc in enumerate(world):
		for key in proc[KEYS]:
			edges += 1
			dot.edge(name(pi), name(key), color="black")

	print(edges)
	#if edges > 3:# and len(edges) > len(world)-2:
	if True:
		fname = str(int(time()*10000))
		with open("graphs/"+fname+".txt", "w+") as f:
			f.write(startcode)
		dot.render("graphs/"+fname, view=True)
