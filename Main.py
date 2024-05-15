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


   # Create a folder to store the instances if it does not exist
   Path_To_Save_Solutions = "./Solution/"  
   basic_path = os.path.join(Path_To_Save_Solutions, "Basic/")
   extended_path = os.path.join(Path_To_Save_Solutions, "Extended/")
   grasp_path = os.path.join(Path_To_Save_Solutions, "Grasp/")
   #if not os.path.exists(Path_To_Save_Solutions):
   #   os.makedirs(Path_To_Save_Solutions)

   if not os.path.exists(basic_path):
      os.makedirs(basic_path)

   if not os.path.exists(extended_path):
      os.makedirs(extended_path)

   if not os.path.exists(grasp_path):
      os.makedirs(grasp_path)

   if len(sys.argv) < 2: 
      print("Missing arguments")
      exit(1)
   
   sfile = sys.argv[1]
  
   inst = Instance(sfile)
   inst_name = "_".join(os.path.basename(sfile).split("_")[:5])
   solu = Solution(inst)
   
   mipBasic = BasicMIPmodel(inst)
   #basic_sol_infos = mipBasic.solveBasic(8,60)
   
   GF = int(sys.argv[2])
   mipExtended = ExtendedMIPmodel(inst,GF)
   mipExtended.solveExtendedWarmStart(mipBasic.mdl,8,600)
   #extended_sol_infos = mipExtended.solveExtended(8,600)
   exit(1)
 
   if len(sys.argv) < 3: 
      # solving basic model and storing the solution
      mipBasic = BasicMIPmodel(inst)
      basic_sol_infos = mipBasic.solveBasic(8,60)
      basic_sol_infos.insert(0, os.path.basename(sfile))
      solu.write_solution(basic_path + inst_name[:-2], basic_sol_infos)
      #solu.write_solution(basic_path + os.path.basename(sfile), basic_sol_infos)

      # solving the grasp and storing the solution
      alg = Algorithm(inst)
      alg.greedyConstructive(solu)
      grasp = GRASP(inst,mipBasic,0.2,5,5)  # 0.2 -> alpha, 5 -> iterations, 5 -> time local search
   
      graspTime= time.time()
      best = grasp.run(solu)
      graspTime= round((time.time() - graspTime), 2)

      totalV = [0] * inst.nV
      for d in range(inst.nNodes):
         for v in range(inst.nV):
            if best.flowD[d][v] > -1:
               totalV[v] = totalV[v] + 1

      grasp_sol_infos = [sum(totalV), best.smdp, best.tmp, best.fo, graspTime]
      grasp_sol_infos.insert(0, os.path.basename(sfile))
      solu.write_solution(grasp_path + inst_name[:-2], grasp_sol_infos)
      #solu.write_solution(grasp_path + os.path.basename(sfile), grasp_sol_infos)

      print(sfile, ";GRASP solution:;",best.fo,";smdp;",best.smdp,";tmp;",best.tmp,";total Items;",sum(totalV),";Time;",graspTime)

   else:
      GF = int(sys.argv[2])
      if GF > inst.nFlows or GF < 0:
         print("percentage of given flows out of bounds")
         exit(1)

      # solve the extended model and store the solution
      mipExtended = ExtendedMIPmodel(inst,GF)
      extended_sol_infos = mipExtended.solveExtended(8,120)
      extended_sol_infos.insert(0, os.path.basename(sfile))
      solu.write_solution(extended_path + inst_name[:-2] + "_" + str(GF), extended_sol_infos)
      #solu.write_solution(extended_path + os.path.basename(sfile) + "_" + str(GF), extended_sol_infos)

   ############################################################
   






