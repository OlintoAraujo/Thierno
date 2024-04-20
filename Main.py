import sys
from Algorithm import *
from Instance import *
from Solution import *
from MIPmodel import *

if __name__ == "__main__":

    #  path instance file
     sfile = sys.argv[1]
    
     inst = Instance(sfile)
     inst.printI()

     solu = Solution(inst)
     print("\n\n")

     alg = Algorithm(inst)
     alg.greedyConstructive(solu)
     solu.printS()     
     
     mip = MIPmodel(inst)
     mip.export_lp("basicModel.lp")
