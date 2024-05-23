import math
import random
import copy
from Instance import *
from Solution import *
from MIPmodel import *

class GRASP:
   def __init__(self, inst :Instance, mipLS :BasicMIPmodel, alpha :float, iterMax :int, timeSubProb :float):
      self.mipLS = mipLS
      self.inst: Instance = inst
      
      self.alpha = alpha 
      self.iterMax = iterMax
      self.timeSubProb = timeSubProb      

      self.gList = []

      for m in range(self.inst.nM):
         for p in range(len(self.inst.Rms[m])) :
            tSizeP = 0
            for v in range(len(self.inst.Rms[m][p])):
               tSizeP = tSizeP + self.inst.sV[self.inst.Rms[m][p][v]] 
            if self.inst.Rmt[m][p]:
               eList = [2*len(self.inst.Rms[m][p])/tSizeP, m, p]  
            else:
               eList = [len(self.inst.Rms[m][p])/tSizeP, m, p]  

            self.gList.append(eList) # [ evaluation, m , p ] 

      self.gList = sorted(self.gList,key=lambda x:x[0]) 


   def randomizedGreedy(self,solu: Solution):
      minSizeRCL = 5 
      flowCap = solu.flowCap.copy()
      gList = self.gList.copy()
      sizeGList = len(gList)-1
      
      for i in range(sizeGList,-1,-1):
         rcl = math.ceil(self.alpha * (len(gList)-1))
         if rcl < minSizeRCL :
            if len(gList) < minSizeRCL :
               rcl = len(gList)
            else :   
               rcl =minSizeRCL 
         cand = (len(gList)-1) - random.randint(0,rcl-1)
         m = gList[cand][1]
         p = gList[cand][2]
         del gList[cand]
         
         for d in range(self.inst.nNodes):
            if not self.inst.dmp[d][m][p]: # checks whether device d provides item set P 
               continue  
            flowsV = []
            dmp = 0  # number of collected items from device d
            random.shuffle(self.inst.Rms[m][p])
            for v in self.inst.Rms[m][p]:
               if solu.flowD[d][v] > -1: 
                  dmp = dmp + 1  #item v has already been collected from device d 
               else: 
                  ok = False
                  random.shuffle(self.inst.flowsNode[d])    
                  for f in self.inst.flowsNode[d]:    
                     if self.inst.sV[v] < flowCap[f]:
                        flowCap[f] = flowCap[f] - self.inst.sV[v]
                        flowsV.append([v,f,d])
                        dmp = dmp + 1
                        ok = True
                        break
                  if not ok : 
                     break
            if dmp == len(self.inst.Rms[m][p]): 
               solu.addP(m,p,flowsV)
            else:
               for i in range(len(flowsV)): # restore the flow cap because it was not possible to collect P
                  v = flowsV[i][0]  
                  f = flowsV[i][1]
                  flowCap[f] = flowCap[f] + self.inst.sV[v]

         if self.inst.Rmt[m][p]: # try to collect a temporal dependence package P
             flowsV = []
             dmp = 0  # number of collected items from device d
             random.shuffle(self.inst.Rms[m][p])
             for v in self.inst.Rms[m][p]:
                ok = False
                for d in range(self.inst.nNodes):
                   if not self.inst.isVd[d][v]:  # node d do not provide item v
                      continue   
                   if solu.flowD[d][v] > -1: 
                      dmp = dmp + 1
                      ok = True
                   else: 
                      random.shuffle(self.inst.flowsNode[d])    
                      for f in self.inst.flowsNode[d]:    
                         if self.inst.sV[v] < flowCap[f]:
                            flowCap[f] = flowCap[f] - self.inst.sV[v]
                            flowsV.append([v,f,d])
                            dmp = dmp + 1
                            ok = True
                            break
                   if ok : 
                      break
              
             devices = []
             for i in range(len(flowsV)):   # verify if Item came from the same device
                if not flowsV[i][2] in devices:
                   devices.append(flowsV[i][2])
              
             if len(devices)> 1 and dmp == len(self.inst.Rms[m][p]): 
                solu.addP(m,p,flowsV)
             else:
                for i in range(len(flowsV)): # restore the flow cap because it was not possible to collect P
                   v = flowsV[i][0]  
                   f = flowsV[i][1]
                   flowCap[f] = flowCap[f] + self.inst.sV[v]
 

   def run(self, bestSolu: Solution):
       
      solu = Solution(self.inst) 
      soluGbest = Solution(self.inst)
      bestPhases =[]

      for i in range(self.iterMax):
         
         soluGbest.reset() 

         for k in range(10):
            solu.reset()
            self.randomizedGreedy(solu)
            if solu.fo > soluGbest.fo :
               soluGbest = copy.deepcopy(solu)

         
         phases = self.mipLS.MIPls(soluGbest,self.timeSubProb,3)
         
         if soluGbest.fo > bestSolu.fo:
            bestSolu = copy.deepcopy(soluGbest)
            bestPhases = list(phases)
         
      return [bestSolu, bestPhases]
    
