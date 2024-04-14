from Instance import *

class Solution:
   # __init__ is constructor method for Solution Class
   def __init__(self, inst: Instance): 
       
     self.inst : Instance =  inst 
     self.fo = 0
     self.smdp = 0
     self.tmp = 0
     self.flowCap = inst.flowCap.copy()
  
     
     self.flowD ={}
     for d in range(self.inst.nNodes):
        self.flowD[d] = [-1] * len(self.inst.Vd[d]) 
     
   
   def addP(self, d : int, m : int, p : int, flows : list):
      if self.inst.Rmt[m][p] == 1 :
         self.fo = self.fo + 2*len(self.inst.Rms[m][p])
         self.tmp = self.tmp + 1
      else:   
         self.fo = self.fo + len(self.inst.Rms[m][p])
      self.smdp = self.smdp + 1
      
      for i in range(len(self.inst.Rms[m][p])): 
         v = self.inst.Rms[m][p][i]
         self.flowD[d][v] = flows[i]
         self.flowCap[flows[i]] = self.flowCap[flows[i]] - self.inst.sV[v]
        

   def printS(self):

      print("Objective Function: ",self.fo, "( smdp = ", self.smdp, ", tmp = ",self.tmp,")")    
      print("Flow available capacity: ",self.flowCap)

      print("Flow of collected items: ")
      for d in range(self.inst.nNodes): 
         print("D",d,self.flowD[d])
