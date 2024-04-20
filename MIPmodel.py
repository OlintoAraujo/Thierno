from docplex.mp.model import Model
import numpy as np
import time
from Instance import *


class MIPmodel:
    
   def __init__(self,inst: Instance):
      
      self.inst = inst;     
      
# variables 
      self.mdl = Model('OINTbasic')

      sb = {(m,d,p): self.mdl.binary_var(name='sb_{}_{}_{}'.format(m,d,p)) for m in range(self.inst.nM) \
            for d in range(self.inst.nNodes) for p in range(len(self.inst.Rms[m]))}
      tb = {(m,p): self.mdl.binary_var(name='tb_{}_{}'.format(m,p)) for m in range(self.inst.nM) \
            for p in range(len(self.inst.Rmt[m])) if self.inst.Rmt[m][p] }
      y = {(d,v,f): self.mdl.binary_var(name='y_{}_{}_{}'.format(d,v,f)) for d in range(self.inst.nNodes) \
           for v in range(self.inst.nV) for f in range(self.inst.nFlows)}
            
      s = {(m,d,p): self.mdl.integer_var(name='s_{}_{}_{}'.format(m,d,p)) for m in range(self.inst.nM) \
          for d in range(self.inst.nNodes) for p in range(len(self.inst.Rms[m]))}
            
      t = {(m,p): self.mdl.integer_var(name='t_{}_{}'.format(m,p)) for m in range(self.inst.nM) \
          for p in range(len(self.inst.Rmt[m])) if self.inst.Rmt[m][p] }

# Constraints 
       # a single telemetry item should be a collected by a single flow
      for d in range(self.inst.nNodes):
         for v in self.inst.Vd[d]:
            self.mdl.add_constraint(self.mdl.sum(y[d, v, f] for f in range(self.inst.nFlows)) <=1, \
                                    ctname=f'collect_{d,v}')

      # capacity of given flows should not be exceeded
      for f in range(self.inst.nFlows):
         self.mdl.add_constraint(self.mdl.sum(self.inst.sV[v] * y[d, v, f] for d in self.inst.flows[f] \
                            for v in self.inst.Vd[d]) <=  self.inst.flowCap[f],ctname=f'capFlow_{f}')
    
      # counting spatial dependencies
      for m in range(self.inst.nM):
         for d in range(self.inst.nNodes):
            for p in range(len(self.inst.Rms[m])):
               if self.inst.dmp[d][m][p]: # True if device d gives the package P to appliation m
                  self.mdl.add_constraint(s[m,d,p] == self.mdl.sum(y[d, v, f] \
                  for v in self.inst.Rms[m][p] if v in self.inst.Vd[d]\
                  for f in range(self.inst.nFlows) if d in self.inst.flows[f] ),ctname=f'smdp{m,d,p}')
      # spatial dependencies
      for m in range(self.inst.nM):
         for d in range(self.inst.nNodes):
            for p in range(len(self.inst.Rms[m])):
               if self.inst.dmp[d][m][p]: # True if device d gives the package P to appliation m
                  self.mdl.add_constraint(sb[m,d,p] * len(self.inst.Rms[m][p])  <= s[m,d,p],\
                  ctname=f'sb{m,d,p}')
      # counting temporal
      for m in range(self.inst.nM):
         for p in range(len(self.inst.Rms[m])):
            if self.inst.Rmt[m][p]:  
               self.mdl.add_constraint(t[m,p] == self.mdl.sum(y[d, v, f] \
               for d in range(self.inst.nNodes) if self.inst.dmp[d][m][p]\
               for v in self.inst.Rms[m][p] if v in self.inst.Vd[d]\
               for f in range(self.inst.nFlows) if d in self.inst.flows[f]), ctname=f't{m,p}')
      # temporal dependencies
      for m in range(self.inst.nM):
         for p in range(len(self.inst.Rms[m])):
            if self.inst.Rmt[m][p]:  
               self.mdl.add_constraint(tb[m,p] * len(self.inst.Rms[m][p]) <= t[m,p],ctname=f'tb{m,p}')
      # the objective function
      obj_function = self.mdl.sum(sb[m,d,p] for m in range(self.inst.nM) \
      for p in range(len(self.inst.Rms[m]))  \
      for d in range(self.inst.nNodes) if self.inst.dmp[d][m][p]) +\
      self.mdl.sum(tb[m,p] for m in range(self.inst.nM)\
      for p in range(len(self.inst.Rms[m])) if self.inst.Rmt[m][p])
      
      self.mdl.maximize(obj_function)


   def export_lp(self, filename: str):
      self.mdl.export_as_lp(filename)
