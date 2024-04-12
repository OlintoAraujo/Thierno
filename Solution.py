from Instance import *

class Solution:
   # __init__ is constructor method for Solution Class
   def __init__(self, inst: Instance): 
       
     self.inst : Instance =  inst 
     self.fo = 0
     self.flowCap = inst.flowCap.copy()
   
     
     self.collectedD ={}
     self.uncollectedD ={}
     self.flowD ={}
     for d in range(self.inst.nNodes):
        self.collectedD[d] = [] 
        self.uncollectedD[d] = self.inst.Vd[d].copy() 
        self.flowD[d] = [-1] * len(self.inst.Vd[d]) 
     
    
   def printS(self):

      print("Objective Function: ",self.fo)    
      print("Flow available capacity: ",self.flowCap)

      print("Collected Items:"); 
      for d in range(self.inst.nNodes): 
         print("D",d,": Collected",self.collectedD[d])

      print("Uncollected Items:"); 
      for d in range(self.inst.nNodes): 
         print("D",d,": uncollected",self.uncollectedD[d])

      print("Flow of collected items: ")
      for d in range(self.inst.nNodes): 
         print("D",d,self.flowD[d])
