import sys
import random
import docplex
import time
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
  
   inst = Instance(sfile)
   
   if len(sys.argv) < 3: 
      GF =  inst.nFlows
   else:
      GF = int(sys.argv[2])
      if GF > inst.nFlows or GF < 0:
         print("percentage of given flows out of bounds")
         exit(1)

   inst = Instance(sfile)
   #inst.printI()
   solu = Solution(inst)

   alg = Algorithm(inst)
   alg.greedyConstructive(solu)
#   print("Initial Solution, Objective Function Value:",solu.fo,"\n")
   
   mip = MIPmodel(inst,GF)
#   mip.MIPls(solu,5,2)
#   print("\nAfter MIP Local Search, Objective Function Value:",solu.fo)
   
   grasp = GRASP(inst,mip,0.2,5,5)
   
   graspTime= time.time()
   best = grasp.run(solu)
   graspTime= time.time() - graspTime

   totalV = [0] * inst.nV
   for d in range(inst.nNodes):
      for v in range(inst.nV):
         if best.flowD[d][v] > -1:
            totalV[v] = totalV[v] + 1

   print(sfile, ";GRASP solution:;",best.fo,";smdp;",best.smdp,";tmp;",best.tmp,";total Items;",sum(totalV),";Time;",graspTime)






