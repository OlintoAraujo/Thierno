from Instance import *

class Solution:
   # __init__ is constructor method for Solution Class
   def __init__(self, inst: Instance): 
       
     self.inst : Instance =  inst 
     self.fo = 0
     self.smdp = 0
     self.tmp = 0
     self.flowCap = inst.flowCap.copy()
     self.collectedItems = [False] * self.inst.nV

     self.flowD ={}
     for d in range(self.inst.nNodes):
        self.flowD[d] = [-2] * self.inst.nV 
        for v in self.inst.Vd[d]:
           self.flowD[d][v] = -1 
    
     self.collectedRm ={}
     for m in range(self.inst.nM):
        self.collectedRm[m] = [0] * len(self.inst.Rms[m])  

     self.collectedRt ={}
     for m in range(self.inst.nM):
        self.collectedRt[m] = [False] * len(self.inst.Rms[m])  

   
   def addP(self, typeP : int, m : int, p : int, flows : list):# typeP :  0 Rms or Rmt (need to check);   1 Rmt (only)
      ok = False
      if typeP == 0 : 
         ok = True
         self.fo = self.fo + 1 
         self.smdp = self.smdp + 1
         self.collectedRm[m][p] = self.collectedRm[m][p] + 1 
    
      if self.inst.Rmt[m][p] and not(self.collectedRt[m][p]):
         ok = True
         self.collectedRt[m][p] = True
         self.fo = self.fo+1
         self.tmp = self.tmp + 1

      if ok : 
         for i in range(len(flows)): 
            v = flows[i][0]
            f = flows[i][1]
            d = flows[i][2]
            self.collectedItems[v] = True
            self.flowCap[f] = self.flowCap[f] - self.inst.sV[v]
            self.flowD[d][v] = f

   def reset(self):
      self.fo = 0
      self.smdp = 0
      self.tmp = 0
      self.flowCap = self.inst.flowCap.copy()
      self.collectedItems = [False] * self.inst.nV
      
 
      for d in range(self.inst.nNodes):
         self.flowD[d] = [-2] * self.inst.nV 
         for v in self.inst.Vd[d]:
            self.flowD[d][v] = -1 
     
      for m in range(self.inst.nM):
         self.collectedRm[m] = [0] * len(self.inst.Rms[m])  

      for m in range(self.inst.nM):
         self.collectedRt[m] = [False] * len(self.inst.Rms[m])  

  
   def printS(self):

      print("Objective Function: ",self.fo, "( smdp = ", self.smdp, ", tmp = ",self.tmp,")")    
      print("Flow available capacity: ",self.flowCap)

      print("Flow of collected items: ")
      for d in range(self.inst.nNodes): 
         print("D",d,self.flowD[d])

      print("Collected P in Rm:")
      for m in range(self.inst.nM):
         print("Application ",m,":",self.collectedRm[m])  
      
      print("Collected P in Rt:")
      for m in range(self.inst.nM):
         print("Application ",m,":",self.collectedRt[m])  


