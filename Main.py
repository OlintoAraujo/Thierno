import sys
from Algorithm import *
from Instance import *
from Solution import *
from MIPmodel import *
from GenInst import *

if __name__ == "__main__":

   nNodes = int(sys.argv[1])
   nFlows = int(sys.argv[2])
   nV = int(sys.argv[3])
   nM = int(sys.argv[4])
   min_capacity = int(sys.argv[5])
   max_capacity = int(sys.argv[6])
   inst = NetworkGenerator(nNodes, nFlows, nV, nM, min_capacity, max_capacity)    #  path instance file
   #sfile = sys.argv[1]
   
   #inst = Instance(sfile)
   #inst.printI()

   solu = Solution(inst)

   alg = Algorithm(inst)
   alg.greedyConstructive(solu)
   print("Initial Solution, Objective Function Value:",solu.fo,"\n")
   
   mip = MIPmodel(inst)
   mip.MIPls(solu)
   print("\nAfter MIP Local Search, Objective Function Value:",solu.fo)

