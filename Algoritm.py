
from Instance import *
from Solution import *

class Algoritm:
    def __init__(self, inst: Instance):
        
        self.inst: Instance = inst

    
    def greedyConstructive(self, solu : Solution):
       gList = []

       for m in range(self.inst.nM):
          for p in range(len(self.inst.Rms[m])) :
             tSizeP = 0
             for v in range(len(self.inst.Rms[m][p])):
                tSizeP = tSizeP + self.inst.sV[self.inst.Rms[m][p][v]] 
             if self.inst.Rmt[m][p] == 1:
                eList = [2*len(self.inst.Rms[m][p])/tSizeP, m, p]  
             else:
                eList = [len(self.inst.Rms[m][p])/tSizeP, m, p]  

             gList.append(eList) # [ evaluation, m , p ] 

       gList = sorted(gList,key=lambda x:x[0], reverse=True) 

       flowCap = solu.flowCap.copy()
       for i in range(len(gList)):
          m = gList[i][1]
          p = gList[i][2]
          for d in range(self.inst.nNodes):
             if not(self.inst.dmp[d][m][p]): # checks whether device d provides item set P 
                continue
             flowsV = []
             dmp = 0  # number of collected items from device d
             for v in self.inst.Rms[m][p]:
                if solu.flowD[d][v] > -1: 
                   dmp = dmp + 1
                else: 
                   ok = False
                   for f in self.inst.flowsNode[d]:    
                      if self.inst.sV[v] < flowCap[f]:
                         flowCap[f] = flowCap[f] - self.inst.sV[v]
                         flowsV.append([v,f])
                         dmp = dmp + 1
                         ok = True
                         break
                   if not ok : 
                      break
                      
             if dmp == len(self.inst.Rms[m][p]):
                solu.addP(d,m,p,flowsV)
       
                
    
