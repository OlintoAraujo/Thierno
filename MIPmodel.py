#from docplex.mp.progress import *
from docplex.mp.model import Model
import numpy as np
import time
from Instance import *
from Solution import *


class MIPmodel:
    
   def __init__(self,inst: Instance):
      
      self.inst = inst;     
      
# variables 
      self.mdl = Model('OINTbasic')
      self.sb = {(m,d,p): self.mdl.binary_var(name='sb_{}_{}_{}'.format(m,d,p)) for m in range(self.inst.nM) \
            for d in range(self.inst.nNodes) for p in range(len(self.inst.Rms[m])) if self.inst.dmp[d][m][p]}

      self.tb = {(m,p): self.mdl.binary_var(name='tb_{}_{}'.format(m,p)) for m in range(self.inst.nM) \
            for p in range(len(self.inst.Rmt[m])) if self.inst.Rmt[m][p] }
      
      self.y = {(d,v,f): self.mdl.binary_var(name='y_{}_{}_{}'.format(d,v,f) ) for d in range(self.inst.nNodes) \
           for v in self.inst.Vd[d] for f in range(self.inst.nFlows) if f in self.inst.flowsNode[d]}
      
      s = {(m,d,p): self.mdl.integer_var(name='s_{}_{}_{}'.format(m,d,p)) for m in range(self.inst.nM) \
          for d in range(self.inst.nNodes) for p in range(len(self.inst.Rms[m])) if self.inst.dmp[d][m][p]}
      
      t = {(m,p): self.mdl.integer_var(name='t_{}_{}'.format(m,p)) for m in range(self.inst.nM) \
          for p in range(len(self.inst.Rmt[m])) if self.inst.Rmt[m][p] }
      
      w = {(m,p,v): self.mdl.binary_var(name='w_{}_{}_{}'.format(m,p,v)) for m in range(self.inst.nM) \
          for p in range(len(self.inst.Rms[m])) if self.inst.Rmt[m][p] \
          for v in self.inst.Rms[m][p] }

# Constraints 
       # a single telemetry item should be a collected by a single flow
      for d in range(self.inst.nNodes):
         for v in self.inst.Vd[d]:
            self.mdl.add_constraint(self.mdl.sum(self.y[d, v, f] for f in self.inst.flowsNode[d]) <=1, \
                                    ctname=f'collect_{d,v}')

      # capacity of given flows should not be exceeded
      for f in range(self.inst.nFlows):
         self.mdl.add_constraint(self.mdl.sum(self.inst.sV[v] * self.y[d, v, f] for d in self.inst.flows[f] \
                            for v in self.inst.Vd[d]) <=  self.inst.flowCap[f],ctname=f'capFlow_{f}')
      
      # counting spatial dependencies
      for m in range(self.inst.nM):
         for d in range(self.inst.nNodes):
            for p in range(len(self.inst.Rms[m])):
               if self.inst.dmp[d][m][p]: # True if device d gives the package P to appliation m
                  self.mdl.add_constraint(s[m,d,p] == self.mdl.sum(self.y[d, v, f] \
                  for v in self.inst.Rms[m][p] if v in self.inst.Vd[d]\
                  for f in range(self.inst.nFlows) if d in self.inst.flows[f] ),ctname=f'smdp{m,d,p}')

      # spatial dependencies
      for m in range(self.inst.nM):
         for d in range(self.inst.nNodes):
            for p in range(len(self.inst.Rms[m])):
               if self.inst.dmp[d][m][p]: # True if device d gives the package P to appliation m
                  self.mdl.add_constraint(self.sb[m,d,p] * len(self.inst.Rms[m][p])  <= s[m,d,p],\
                  ctname=f'sb{m,d,p}')
     
      # couting temporal 1
      for m in range(self.inst.nM):
         for p in range(len(self.inst.Rms[m])):
            if self.inst.Rmt[m][p]:
               for v in self.inst.Rms[m][p]:
                  self.mdl.add_constraint(w[m, p, v] <= self.mdl.sum(self.y[d, v, f] \
                  for d in range(self.inst.nNodes) if self.inst.dmp[d][m][p] \
                  for f in self.inst.flowsNode[d]),ctname=f'w{m,p,v}')   
 
      # counting temporal 2
      for m in range(self.inst.nM):
         for p in range(len(self.inst.Rms[m])):
            if self.inst.Rmt[m][p]:  
               self.mdl.add_constraint(t[m,p] == self.mdl.sum(w[m, p, v] \
               for v in self.inst.Rms[m][p]), ctname=f't{m,p}')
      
      # temporal dependencies
      for m in range(self.inst.nM):
         for p in range(len(self.inst.Rms[m])):
            if self.inst.Rmt[m][p]:  
               self.mdl.add_constraint(self.tb[m,p] * len(self.inst.Rms[m][p]) <= t[m,p],ctname=f'tb{m,p}')
      
# the objective function
      obj_function = self.mdl.sum(self.sb[m,d,p] for m in range(self.inst.nM) \
      for p in range(len(self.inst.Rms[m]))  \
      for d in range(self.inst.nNodes) if self.inst.dmp[d][m][p]) +\
      self.mdl.sum(self.tb[m,p] for m in range(self.inst.nM)\
      for p in range(len(self.inst.Rms[m])) if self.inst.Rmt[m][p])
      
      self.mdl.maximize(obj_function)
      self.export_lp('basicModel.lp')

   def export_lp(self, filename: str):
      self.mdl.export_as_lp(filename)

   
   def MIPls(self, solu: Solution):
      #print("\n\n==================================\nInitial Solution: ",solu.fo)
      # Phase 1  :  Try collect news P's fixing the initial solution

      self.mdl.parameters.timelimit.set(10)

      for d in range(self.inst.nNodes):
         for v in range(self.inst.nV):
            if solu.flowD[d][v] > -1:
               self.y[d,v,solu.flowD[d][v]].lb = 1

#      self.mdl.parameters.timelimit.set(600) 
      sol1 = self.mdl.solve()
      for d in range(self.inst.nNodes):
         for v in range(self.inst.nV):
            if solu.flowD[d][v] > -1:
               self.y[d,v,solu.flowD[d][v]].lb = 0

      print("Local Search Phase 1: ",sol1.objective_value)

      # Phase 2  : Trying to collect new sets P's by fixing devices and items, choosing new paths to collect items 
      yd = sol1.get_value_dict(self.y, keep_zeros=False)
      indices = [chave for chave, valor in yd.items() if valor == 1]
      
      lsPhase2 = {}
      for e in indices:
         d = e[0]
         v = e[1]
         lsPhase2[e] = self.mdl.add_constraint(self.mdl.sum(self.y[d,v,f] for f in self.inst.flowsNode[d]) ==1,\
                                    ctname=f'ls2_{d,v}')
      sol2 = self.mdl.solve()
      for e in indices:
         self.mdl.remove_constraint(lsPhase2[e])
      print("Local Search Phase 2: ",sol2.objective_value)

      # Phase 3  : Trying to collect new sets P by fixing items, choosing devices and paths to collect the items 

      yd = sol2.get_value_dict(self.y, keep_zeros=False)
      indices = [chave for chave, valor in yd.items() if valor == 1]

      items = [0] * self.inst.nV

      for e in indices:
         v = e[1]
         items[v] = items[v]+1

      lsPhase3 = {}
      for v in range(self.inst.nV):
         if items[v] == 0: 
            continue
         lsPhase3[v] = self.mdl.add_constraint(self.mdl.sum(self.y[d, v, f] \
         for d in range(self.inst.nNodes) if v in self.inst.Vd[d]\
         for f in self.inst.flowsNode[d]) >=items[v], ctname=f'ls3_{v}')
      sol3 = self.mdl.solve()
      print("Local Search Phase 3: ",sol3.objective_value)

      for v in lsPhase3:
         self.mdl.remove_constraint(lsPhase3[v])

       # update solution
      solu.reset()
      for d in range(self.inst.nNodes):
         for v in self.inst.Vd[d]:
            for f in self.inst.flowsNode[d]:
               if self.y[d,v,f].solution_value >= 0.5:
                  solu.flowCap[f] = solu.flowCap[f] - self.inst.sV[v]
                  solu.flowD[d][v] = f

      for m in range(self.inst.nM):
         for d in range(self.inst.nNodes):
            for p in range(len(self.inst.Rms[m])):
               if self.inst.dmp[d][m][p]:
                  if self.sb[m,d,p].solution_value >= 0.5:
                     solu.fo = solu.fo+1
                     solu.smdp = solu.smdp+1
                     solu.collectedRm[m][p] = solu.collectedRm[m][p] + 1 
                     if self.inst.Rmt[m][p] and not solu.collectedRt[m][p]:
                        solu.tmp = solu.tmp+1
                        solu.fo = solu.fo + 1
                        solu.collectedRt[m][p] = True
      
      for m in range(self.inst.nM):
            for p in range(len(self.inst.Rms[m])):
               if self.inst.Rmt[m][p]:
                  if self.tb[m,p].solution_value >= 0.5:
                     if self.inst.Rmt[m][p] and not solu.collectedRt[m][p]:
                        solu.tmp = solu.tmp+1
                        solu.fo = solu.fo + 1
                        solu.collectedRt[m][p] = True
      
#================================================
#teste.active = False
#teste.lhs=d=teste.lhs-self.y[0,0,0]+2*self.y[0,0,0] 
# teste.rhs = 100
#self.mdl.remove_constraint(teste)
#      yd = sol.get_value_dict(self.y, keep_zeros=False)
#      xd = sol.get_value_dict(self.y, keep_zeros=False)

#      chaves_valor_1 = [chave for chave, valor in xd.items() if valor == 1]

#      print(chaves_valor_1)
#      print(chaves_valor_1[0][0])
#      print(sol.objective_value)
#      self.export_lp('basicModel.lp')
#      sol2 = self.mdl.solve()
#      print("Local Search Phase 2: ",sol2.objective_value)


      # update solution

