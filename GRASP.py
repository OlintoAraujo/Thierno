
from Instance import *
from Solution import *
from MIPmodel import *

class GRASP:
   def __init__(self, inst: Instance, mipLS : MIPmodel):
      self.mipLS = mipLS
      self.inst: Instance = inst
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


   def greedy(self,solu: Solution):
      
      flowCap = solu.flowCap.copy()
#      for i in range(len(gList)-1,-1,-1):
#         m = gList[i][1]
#         p = gList[i][2]
#         for d in range(self.inst.nNodes):
#            if not self.inst.dmp[d][m][p]: # checks whether device d provides item set P 
#               continue  
#            flowsV = []
#            dmp = 0  # number of collected items from device d
#            for v in self.inst.Rms[m][p]:
#               if solu.flowD[d][v] > -1: 
#                  dmp = dmp + 1  #item v has already been collected from device d 
#               else: 
#                  ok = False
#                  for f in self.inst.flowsNode[d]:    
#                     if self.inst.sV[v] < flowCap[f]:
#                        flowCap[f] = flowCap[f] - self.inst.sV[v]
#                        flowsV.append([v,f,d])
#                        dmp = dmp + 1
#                        ok = True
#                        break
#                  if not ok : 
#                     break
#            if dmp == len(self.inst.Rms[m][p]): 
#               solu.addP(0,m,p,flowsV)
#            else:
#               for i in range(len(flowsV)): # restore the flow cap because it was not possible to collect P
#                  v = flowsV[i][0]  
#                  f = flowsV[i][1]
#                  flowCap[f] = flowCap[f] + self.inst.sV[v]
#
#         if self.inst.Rmt[m][p] and not solu.collectedRt[m][p]: # try to collect a temporal dependence package P
#             flowsV = []
#             dmp = 0  # number of collected items from device d
#             for v in self.inst.Rms[m][p]:
#                ok = False
#                for d in range(self.inst.nNodes):
#                   if not self.inst.isVd[d][v]:  # node d do not provide item v
#                      continue   
#                   if solu.flowD[d][v] > -1: 
#                      dmp = dmp + 1
#                      ok = True
#                   else: 
#                      for f in self.inst.flowsNode[d]:    
#                         if self.inst.sV[v] < flowCap[f]:
#                            flowCap[f] = flowCap[f] - self.inst.sV[v]
#                            flowsV.append([v,f,d])
#                            dmp = dmp + 1
#                            ok = True
#                            break
#                   if ok : 
#                      break
#             if dmp == len(self.inst.Rms[m][p]): 
#                solu.addP(1,m,p,flowsV)
#             else:
#                for i in range(len(flowsV)): # restore the flow cap because it was not possible to collect P
#                   v = flowsV[i][0]  
#                   f = flowsV[i][1]
#                   flowCap[f] = flowCap[f] + self.inst.sV[v]
 
 

   def run(self, solu: Solution):
      print("GRASP")
   
      iterMax = 3

      for i in range(iterMax):
         solu.reset()
         self.greedy(solu)
         print(i,")",solu.fo) 
         

    
