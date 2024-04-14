
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

             gList.append(eList) 

       gList = sorted(gList,key=lambda x:x[0], reverse=True) 

       for i in range(len(gList)):
          m = gList[i][1]
          p = gList[i][2]
          for d in range(self.inst.nNodes):
             if not(self.inst.dmp[d][m][p]): 
                continue
             flowsV = [] 
             for v in range(len(self.inst.Rms[m][p])):
                for f in range(self.inst.nFlows):
                   if self.inst.sV[v] < solu.flowCap[f]:
                      flowsV.append(f)
                      break 
                      
             if len(flowsV) == len(self.inst.Rms[m][p]):
                solu.addP(d,m,p,flowsV)
       solu.printS()
       
                
    
