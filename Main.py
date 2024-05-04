import sys
import random
from Algorithm import *
from Instance import *
from Solution import *
from MIPmodel import *
from GenInst import *
from GRASP import *

if __name__ == "__main__":

   #seed = 2023
   #random.seed(seed)
   random.seed()

   if len(sys.argv) < 2: 
      print("Missing arguments")
      exit(1)
   
   sfile = sys.argv[1]
  
   sNetFile = ""
   if len(sys.argv) > 2: 
      sNetFile = sys.argv[2]
  
   print("====================================",sNetFile)
   inst = Instance(sfile,sNetFile)
   inst.printI()
   solu = Solution(inst)

#   alg = Algorithm(inst)
#   alg.greedyConstructive(solu)
#   print("Initial Solution, Objective Function Value:",solu.fo,"\n")
   
   mip = MIPmodel(inst)
#   mip.MIPls(solu,5,2)
#   print("\nAfter MIP Local Search, Objective Function Value:",solu.fo)

   grasp = GRASP(inst,mip,0.1,5,3)
   grasp.run(solu)
