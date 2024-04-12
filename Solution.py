from Instance import *

class Solution:
   # __init__ is constructor method for Solution Class
   def __init__(self, inst: Instance): 
       
     self.inst : Instance =  inst 
     self.fo = 0
     self.flowCap = inst.flowCap.copy()

    
   def printS(self):

      print("Objective Function: ",self.fo)    
      print("Flow available capacity: ",self.flowCap)
