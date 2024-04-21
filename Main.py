import sys
from Algorithm import *
from Instance import *
from Solution import *
from MIPmodel import *

if __name__ == "__main__":

    #  path instance file
     sfile = sys.argv[1]
    
     inst = Instance(sfile)
     #inst.printI()

     solu = Solution(inst)

     alg = Algorithm(inst)
     alg.greedyConstructive(solu)
     print("Initial Solution, Objective Function Value:",solu.fo,"\n")
     
     mip = MIPmodel(inst)
     mip.MIPls(solu)
     print("\nAfter MIP Local Search, Objective Function Value:",solu.fo)

