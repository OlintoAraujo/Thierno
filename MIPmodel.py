#from docplex.mp.progress import *
from docplex.mp.model import Model
import numpy as np
import time
from Instance import *
from Solution import *
import math

class MIPmodel:
    
   def __init__(self,inst: Instance, GF: int):
      
      self.inst = inst     
      self.GF = GF
# ===================================== Basic Model      
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
      
      self.mdl.export_as_lp('basicModel.lp')
   
# ===================================== Extended Model   
      if self.GF < self.inst.nFlows:
         calculatedFlows = self.inst.nFlows - GF
         
         cFlows = [i for i in range(calculatedFlows)]
         gFlows = [i for i in range(calculatedFlows,self.inst.nFlows)]

         startNode = []
         endNode = []
         for f in cFlows:
            startNode.append(self.inst.flows[f][0])
            endNode.append(self.inst.flows[f][len(self.inst.flows[f])-1])

         self.mdlE = Model('OINTextended')
         self.sbe = {(m,d,p): self.mdlE.binary_var(name='sb_{}_{}_{}'.format(m,d,p)) for m in range(self.inst.nM) \
               for d in range(self.inst.nNodes) for p in range(len(self.inst.Rms[m])) if self.inst.dmp[d][m][p]}
   
         self.tbe = {(m,p): self.mdlE.binary_var(name='tb_{}_{}'.format(m,p)) for m in range(self.inst.nM) \
               for p in range(len(self.inst.Rmt[m])) if self.inst.Rmt[m][p] }
        
         ubYe = {} 
         for d in range(self.inst.nNodes):
            for v in self.inst.Vd[d]:
               for f in range(self.inst.nFlows):
                  if f in cFlows  or f in self.inst.flowsNode[d]:
                     ubYe[(d,v,f)] = 1
                  else:
                     ubYe[(d,v,f)] = 0 
         
         self.ye = {(d,v,f): self.mdlE.integer_var(name='y_{}_{}_{}'.format(d,v,f), lb = 0, ub = ubYe[(d,v,f)]  )  \
         for d in range(self.inst.nNodes) for v in self.inst.Vd[d] for f in range(self.inst.nFlows)}
         
         se = {(m,d,p): self.mdlE.integer_var(name='s_{}_{}_{}'.format(m,d,p)) for m in range(self.inst.nM) \
             for d in range(self.inst.nNodes) for p in range(len(self.inst.Rms[m])) if self.inst.dmp[d][m][p]}
         
         te = {(m,p): self.mdlE.integer_var(name='t_{}_{}'.format(m,p)) for m in range(self.inst.nM) \
             for p in range(len(self.inst.Rmt[m])) if self.inst.Rmt[m][p] }
         
         we = {(m,p,v): self.mdlE.binary_var(name='w_{}_{}_{}'.format(m,p,v)) for m in range(self.inst.nM) \
             for p in range(len(self.inst.Rms[m])) if self.inst.Rmt[m][p] \
             for v in self.inst.Rms[m][p] }
   
         xe = {(self.inst.arcs[k][0],self.inst.arcs[k][1],f):\
              self.mdlE.integer_var(name='x_{}_{}_{}'.format(self.inst.arcs[k][0],self.inst.arcs[k][1],f),\
              lb =0,ub = int(self.inst.arcs[k][0] != endNode[f])) \
              for k in range(self.inst.nArcs) for f in cFlows}
         
         x2e = {(self.inst.arcs[k][0],self.inst.arcs[k][1],f):\
              self.mdlE.integer_var(name='x2_{}_{}_{}'.format(self.inst.arcs[k][0],self.inst.arcs[k][1],f),\
              lb=0,ub= self.inst.flowCap[f] * (self.inst.arcs[k][0] != endNode[f]) ) \
              for k in range(self.inst.nArcs) for f in cFlows}
          
         z = {(f): self.mdlE.binary_var(name='z_{}'.format(f)) for f in cFlows}

         # add constraints
         for f in cFlows:
            self.mdlE.add_constraint(self.mdlE.sum(xe[startNode[f], self.inst.arcs[k][1], f] \
            for k in range(self.inst.nArcs) if self.inst.arcs[k][0] == startNode[f]) == 1\
            , ctname=f'startPath{f}')
            
            self.mdlE.add_constraint(self.mdlE.sum(xe[self.inst.arcs[k][0], endNode[f], f] \
            for k in range(self.inst.nArcs) if self.inst.arcs[k][1] == endNode[f]) == 1 \
            , ctname=f'endPath{f}')
			    
         for n in range(self.inst.nNodes):
            for f in cFlows:
               self.mdlE.add_constraint(self.mdlE.sum(xe[n, self.inst.arcs[k][1],f]\
               for k in range(self.inst.nArcs) if self.inst.arcs[k][0] == n) <=1, \
               ctname=f'one{n,f}')

         for f in cFlows:
            self.mdlE.add_constraint(self.mdlE.sum(xe[self.inst.arcs[k][0], self.inst.arcs[k][1],f]\
            for k in range(self.inst.nArcs)) <= \
            self.inst.maxL, \
            ctname=f'maxL{f}')
         
         for d in range(self.inst.nNodes):
            for f in cFlows:  
               if d == startNode[f] or d == endNode[f]:
                  continue
               self.mdlE.add_constraint(self.mdlE.sum(xe[self.inst.arcs[k][0],d,f]\
               for k in range(self.inst.nArcs) if self.inst.arcs[k][1] == d) - \
               self.mdlE.sum(xe[d, self.inst.arcs[k][1],f] \
               for k in range(self.inst.nArcs) if self.inst.arcs[k][0] == d) == 0\
               ,ctname=f'cX_{d,f}')
         
         # Link between network x and network x2
         bigM = 0
         for v in range(self.inst.nV):
            bigM = bigM + self.inst.sV[v]
         bigM = bigM * self.inst.nNodes   

         for f in cFlows:
            for k in range(self.inst.nArcs):
               self.mdlE.add_constraint(x2e[self.inst.arcs[k][0], self.inst.arcs[k][1],f] <= \
               bigM*xe[self.inst.arcs[k][0], self.inst.arcs[k][1],f], \
               ctname=f'x_x2{self.inst.arcs[k][0],self.inst.arcs[k][1],f}')

         for d in range(self.inst.nNodes):
            for f in cFlows:   
               if d == endNode[f]: 
                  continue
               self.mdlE.add_constraint(self.mdlE.sum(x2e[self.inst.arcs[k][0],d,f]\
               for k in range(self.inst.nArcs) if self.inst.arcs[k][1] == d) - \
               self.mdlE.sum(x2e[d, self.inst.arcs[k][1],f] \
               for k in range(self.inst.nArcs) if self.inst.arcs[k][0] == d) == \
               -self.mdlE.sum(self.inst.sV[v]*self.ye[d,v,f] for v in self.inst.Vd[d]),ctname=f'cX2_{d,f}')
        
         for f in cFlows:   
            self.mdlE.add_constraint(self.mdlE.sum(x2e[self.inst.arcs[k][0],endNode[f],f]\
            for k in range(self.inst.nArcs) if self.inst.arcs[k][1] == endNode[f]) == \
            self.mdlE.sum(self.inst.sV[v]*self.ye[d,v,f] for d in range(self.inst.nNodes) \
            for v in self.inst.Vd[d]),ctname=f'Fn_{endNode[f],f}')
        
         # a single telemetry item should be a collected by a single (any) flow
         for d in range(self.inst.nNodes):
            for v in self.inst.Vd[d]:
               self.mdlE.add_constraint(self.mdlE.sum(self.ye[d, v, f] for f in range(self.inst.nFlows)) <=1, \
                                       ctname=f'collect_{d,v}')
         
         # capacity constraint to the given flows
         for f in gFlows:
            self.mdlE.add_constraint(self.mdlE.sum(self.inst.sV[v]*self.ye[d, v, f] \
            for d in self.inst.flows[f]  for v in self.inst.Vd[d]) <=\
            self.inst.flowCap[f],ctname=f'cGF_{f}')
         
         # counting spatial dependencies
         for m in range(self.inst.nM):
            for d in range(self.inst.nNodes):
               for p in range(len(self.inst.Rms[m])):
                  if self.inst.dmp[d][m][p]: # True if device d gives the package P to appliation m
                     self.mdlE.add_constraint(se[m,d,p] == self.mdlE.sum(self.ye[d, v, f] \
                     for v in self.inst.Rms[m][p] if v in self.inst.Vd[d]\
                     for f in range(self.inst.nFlows) if d in self.inst.flows[f] ),ctname=f'smdp{m,d,p}')
   
         # spatial dependencies
         for m in range(self.inst.nM):
            for d in range(self.inst.nNodes):
               for p in range(len(self.inst.Rms[m])):
                  if self.inst.dmp[d][m][p]: # True if device d gives the package P to appliation m
                     self.mdlE.add_constraint(self.sbe[m,d,p] * len(self.inst.Rms[m][p])  <= se[m,d,p],\
                     ctname=f'sb{m,d,p}')
        
         # couting temporal 1
         for m in range(self.inst.nM):
            for p in range(len(self.inst.Rms[m])):
               if self.inst.Rmt[m][p]:
                  for v in self.inst.Rms[m][p]:
                     self.mdlE.add_constraint(we[m, p, v] <= self.mdlE.sum(self.ye[d, v, f] \
                     for d in range(self.inst.nNodes) if self.inst.dmp[d][m][p] \
                     for f in range(self.inst.nFlows)),ctname=f'w{m,p,v}')   
    
         # counting temporal 2
         for m in range(self.inst.nM):
            for p in range(len(self.inst.Rms[m])):
               if self.inst.Rmt[m][p]:  
                  self.mdlE.add_constraint(te[m,p] == self.mdlE.sum(we[m, p, v] \
                  for v in self.inst.Rms[m][p]), ctname=f't{m,p}')
         
         # temporal dependencies
         for m in range(self.inst.nM):
            for p in range(len(self.inst.Rms[m])):
               if self.inst.Rmt[m][p]:  
                  self.mdlE.add_constraint(self.tbe[m,p] * len(self.inst.Rms[m][p]) <= te[m,p],ctname=f'tb{m,p}')
    
# the objective function
         self.epsilon = 0.01
         obj_functionE = self.mdlE.sum(self.sbe[m,d,p] for m in range(self.inst.nM) \
         for p in range(len(self.inst.Rms[m]))  \
         for d in range(self.inst.nNodes) if self.inst.dmp[d][m][p]) +\
         self.mdlE.sum(self.tbe[m,p] for m in range(self.inst.nM)\
         for p in range(len(self.inst.Rms[m])) if self.inst.Rmt[m][p]) - \
         self.epsilon * self.mdlE.sum(xe[self.inst.arcs[k][0],self.inst.arcs[k][1],f] \
         for k in range(self.inst.nArcs) for f in cFlows)
  
         self.mdlE.maximize(obj_functionE)
 
         self.mdlE.export_as_lp('extendedModel.lp')

# ===================================== Extended Model_0

         self.mdlE0 = Model('OINTextended_0')
         # variables
         self.sbe0 = {(m,d,p): self.mdlE0.binary_var(name='sbe0_{}_{}_{}'.format(m,d,p)) for m in range(self.inst.nM) \
            for d in range(self.inst.nNodes) for p in range(len(self.inst.Rms[m])) if self.inst.dmp[d][m][p]}
         self.tbe0 = {(m,p): self.mdlE0.binary_var(name='tbe0_{}_{}'.format(m,p)) for m in range(self.inst.nM) \
            for p in range(len(self.inst.Rmt[m])) if self.inst.Rmt[m][p]}

         ubYe = {} 
         for d in range(self.inst.nNodes):
            for v in self.inst.Vd[d]:
               for f in range(self.inst.nFlows):
                  if f in cFlows  or f in self.inst.flowsNode[d]:
                     ubYe[(d,v,f)] = 1
                  else:
                     ubYe[(d,v,f)] = 0 
         self.ye0 = {(d,v,f): self.mdlE0.integer_var(name='ye0_{}_{}_{}'.format(d,v,f),lb = 0, ub = ubYe[(d,v,f)] ) \
         for d in range(self.inst.nNodes) for v in self.inst.Vd[d] for f in range(self.inst.nFlows)}
         
         self.xe0 = {(self.inst.arcs[k][0],self.inst.arcs[k][1],f):\
                  self.mdlE0.integer_var(name='x_{}_{}_{}'.format(self.inst.arcs[k][0],self.inst.arcs[k][1],f),\
                  lb =0,ub = int(self.inst.arcs[k][0] != endNode[f])) \
                  for k in range(self.inst.nArcs) for f in cFlows}

         gg = {(i,f): self.mdlE0.continuous_var(name='gg_{}_{}'.format(i,f)) for i in range(self.inst.nNodes) \
            for f in range(self.inst.nFlows)}
         se0 = {(m,d,p): self.mdlE0.integer_var(name='se0_{}_{}_{}'.format(m,d,p)) for m in range(self.inst.nM) \
            for d in range(self.inst.nNodes) for p in range(len(self.inst.Rms[m])) if self.inst.dmp[d][m][p]}
         te0 = {(m,p): self.mdlE0.integer_var(name='te0_{}_{}'.format(m,p)) for m in range(self.inst.nM) \
            for p in range(len(self.inst.Rmt[m])) if self.inst.Rmt[m][p]}

         we0 = {(m,p,v): self.mdlE0.binary_var(name='we0_{}_{}_{}'.format(m,p,v)) for m in range(self.inst.nM) \
            for p in range(len(self.inst.Rms[m])) if self.inst.Rmt[m][p] \
            for v in self.inst.Rms[m][p] }

         ze0 = {(f): self.mdlE0.binary_var(name='ze0_{}'.format(f)) for f in cFlows}

         # constraints
         for f in cFlows:
            self.mdlE0.add_constraint(self.mdlE0.sum(self.xe0[startNode[f], self.inst.arcs[k][1], f] \
                  for k in range(self.inst.nArcs) if self.inst.arcs[k][0] == startNode[f]) == 1, ctname=f'startPath{f}' )


            self.mdlE0.add_constraint(self.mdlE0.sum(self.xe0[self.inst.arcs[k][0], endNode[f], f] \
                  for k in range(self.inst.nArcs) if self.inst.arcs[k][1] == endNode[f]) == 1, ctname=f'endPath{f}' )


         for d in range(self.inst.nNodes):
                  for f in cFlows:  
                     if d == startNode[f] or d == endNode[f]:
                        continue
                     self.mdlE0.add_constraint(self.mdlE0.sum(self.xe0[self.inst.arcs[k][0],d,f]\
                     for k in range(self.inst.nArcs) if self.inst.arcs[k][1] == d) - \
                     self.mdlE0.sum(self.xe0[d, self.inst.arcs[k][1],f] \
                     for k in range(self.inst.nArcs) if self.inst.arcs[k][0] == d) == 0\
                     ,ctname=f'cX_{d,f}')

         for i in range(self.inst.nNodes):
            for j in range(self.inst.nNodes):
                  for f in cFlows:
                     if (i,j) in self.inst.arcs:
                        self.mdlE0.add_constraint(self.xe0[i,j,f] + self.xe0[j,i,f] <= 1)


         for i in range(self.inst.nNodes):
            for j in range(self.inst.nNodes):
                  for f in range(self.inst.nFlows):
                     if (i,j) in self.inst.arcs:
                        self.mdlE0.add_constraint(gg[j,f] >= gg[i,f] + 1 - len(range(self.inst.nNodes))*(1-self.xe0[i,j,f]))

         for f in cFlows:
            self.mdlE0.add_constraint(self.mdlE0.sum(self.xe0[self.inst.arcs[k][0], self.inst.arcs[k][1],f] \
                  for k in self.inst.arcs) <= self.inst.maxL ,ctname=f'L{f}')

         for d in range(self.inst.nNodes):
            for v in self.inst.Vd[d]:
                  for f in cFlows:
                     self.mdlE0.add_constraint(self.ye0[d,v,f] <= self.mdlE0.sum(self.xe0[self.inst.arcs[k][0], \
                     self.inst.arcs[k][1],f] for k in self.inst.arcs if self.inst.arcs[k][0] == d),ctname=f'x_y{d,v,f}')

         for d in range(self.inst.nNodes):
            for v in self.inst.Vd[d]:
                  self.mdlE0.add_constraint(self.mdlE0.sum(self.ye0[d, v, f] for f in range(self.inst.nFlows)) <=1)

#         for f in gFlows:
         for f in range(self.inst.nFlows):
            self.mdlE0.add_constraint(self.mdlE0.sum(self.inst.sV[v] * self.ye0[d, v, f] for d in range(self.inst.nNodes) \
            for v in self.inst.Vd[d]) <=  self.inst.flowCap[f],ctname=f'cap{f}')
#            self.mdlE0.add_constraint(self.mdlE0.sum(self.inst.sV[v] * self.ye0[d, v, f] for d in self.inst.flows[f] \
#            for v in self.inst.Vd[d]) <=  self.inst.flowCap[f])
#            self.mdlE0.add_constraint(self.mdlE0.sum(self.ye0[d,v,f] for d in [j for j in range(self.inst.nNodes) \
#            if j not in self.inst.flows[f]] for v in self.inst.Vd[d] ) <= 0)

#         for f in cFlows:
#            self.mdlE0.add_constraint(self.mdlE0.sum(self.inst.sV[v] * self.ye0[d, v, f] for d in range(self.inst.nNodes) \
#            for v in self.inst.Vd[d]) <=  self.inst.flowCap[f])

         for m in range(self.inst.nM):
            for d in range(self.inst.nNodes):
                  for p in range(len(self.inst.Rms[m])):
                     if self.inst.dmp[d][m][p]:
                       self.mdlE0.add_constraint(se0[m,d,p] == self.mdlE0.sum(self.ye0[d, v, f] \
                              for v in self.inst.Vd[d] \
                              for f in range(self.inst.nFlows)))

         for m in range(self.inst.nM):
            for d in range(self.inst.nNodes):
                  for p in range(len(self.inst.Rms[m])):
                     if self.inst.dmp[d][m][p]:
                        self.mdlE0.add_constraint(self.sbe0[m,d,p] <= se0[m,d,p]/len(self.inst.Rms[m][p]))

         # couting temporal 1
         for m in range(self.inst.nM):
            for p in range(len(self.inst.Rms[m])):
               if self.inst.Rmt[m][p]:
                  for v in self.inst.Rms[m][p]:
                     self.mdlE0.add_constraint(we0[m, p, v] <= self.mdlE0.sum(self.ye0[d, v, f] \
                     for d in range(self.inst.nNodes) if self.inst.dmp[d][m][p] \
                     for f in self.inst.flowsNode[d]),ctname=f'we0{m,p,v}')   
    
         # counting temporal 2
         for m in range(self.inst.nM):
            for p in range(len(self.inst.Rms[m])):
               if self.inst.Rmt[m][p]:  
                  self.mdlE0.add_constraint(te0[m,p] == self.mdlE0.sum(we0[m, p, v] \
                  for v in self.inst.Rms[m][p]), ctname=f'te0{m,p}')
      
         # temporal dependencies
         for m in range(self.inst.nM):
            for p in range(len(self.inst.Rms[m])):
               if self.inst.Rmt[m][p]:  
                  self.mdlE0.add_constraint(self.tbe0[m,p] * len(self.inst.Rms[m][p]) <= te0[m,p],ctname=f'tbe0{m,p}')
    
         obj_function = self.mdlE0.sum(self.sbe0[m,d,p] for m in range(self.inst.nM) \
            for d in range(self.inst.nNodes)  \
            for p in range(len(self.inst.Rms[m])) if self.inst.dmp[d][m][p]) \
                  + self.mdlE0.sum(self.tbe0[m,p] for m in range(self.inst.nM) \
            for p in range(len(self.inst.Rms[m])) if self.inst.Rmt[m][p])

         self.mdlE0.maximize(obj_function)

         self.mdlE0.export_as_lp('extendedModel0.lp')


         #self.sol_e0 = self.mdlE0.solve()
         #print(f'Objective value Extended 0: {self.sol_e0.objective_value}')

# ===================================== End Extended Model_0

   
   def MIPls(self, solu: Solution,timeL : int, emphasis : int):
      self.mdl.parameters.timelimit.set(timeL)
      
      # Phase 1  :  Try collect news P's fixing the initial solution
      for d in range(self.inst.nNodes):  # fix initial solution
         for v in range(self.inst.nV):
            if solu.flowD[d][v] > -1:
               self.y[d,v,solu.flowD[d][v]].lb = 1
      
      sol1 = self.mdl.solve()
      
      for d in range(self.inst.nNodes): # release initial solution
         for v in range(self.inst.nV):
            if solu.flowD[d][v] > -1:
               self.y[d,v,solu.flowD[d][v]].lb = 0

      if emphasis > 1 : 
         print("Local Search Phase 1: ",sol1.objective_value)
         
         # Phase 2  : Trying to collect new sets P's by fixing devices and items, choosing new paths to collect items 
         for m in range(self.inst.nM):   # fix solution
            for d in range(self.inst.nNodes):
               for p in range(len(self.inst.Rms[m])):
                  if self.inst.dmp[d][m][p]:
                     if sol1.get_value(self.sb[m,d,p]) > 0.5 : 
                        self.sb[m,d,p].lb  == 1
      
         for m in range(self.inst.nM):
               for p in range(len(self.inst.Rms[m])):
                  if self.inst.Rmt[m][p]:
                     if sol1.get_value(self.tb[m,p]) > 0.5 : 
                        self.tb[m,p].lb  == 1

         sol2 = self.mdl.solve()
         
         for m in range(self.inst.nM):   # release solution
            for d in range(self.inst.nNodes):
               for p in range(len(self.inst.Rms[m])):
                  if self.inst.dmp[d][m][p]:
                     if sol1.get_value(self.sb[m,d,p]) > 0.5 : 
                        self.sb[m,d,p].lb  == 0 
      
         for m in range(self.inst.nM):
               for p in range(len(self.inst.Rms[m])):
                  if self.inst.Rmt[m][p]:
                     if sol1.get_value(self.tb[m,p]) > 0.5 : 
                        self.tb[m,p].lb  == 0  
 
         print("Local Search Phase 2: ",sol2.objective_value)

      # Phase 3  : Trying to collect new sets P by fixing items, choosing devices and paths to collect the items 
      if emphasis > 2: 
         sd = sol2.get_value_dict(self.sb, keep_zeros=False)   # fix solution
         indices = [chave for chave, valor in sd.items() if valor >= 0.5]

         lsPhase30 = {}
         packages ={}
         for m in range(self.inst.nM):
            packages[m] = [0]*len(self.inst.Rms[m])
      
         for e in range(len(indices)):
            m = indices[e][0]
            p = indices[e][2]
            packages[m][p] = packages[m][p] + 1
         
         k = 0
         for m in range(self.inst.nM):
            for p in range(len(self.inst.Rms[m])):
               lsPhase30[k] = self.mdl.add_constraint(self.mdl.sum(self.sb[m,d,p] \
               for d in range(self.inst.nNodes) if self.inst.dmp[d][m][p] ) >=packages[m][p], ctname=f'ls30_{v}')
               k = k + 1
      
         td = sol2.get_value_dict(self.tb, keep_zeros=False)
         indices = [chave for chave, valor in td.items() if valor >= 0.5]

         lsPhase31 = {}
         packages ={}
         for m in range(self.inst.nM):
            packages[m] = [0]*len(self.inst.Rms[m])
      
         for e in range(len(indices)):
            m = indices[e][0]
            p = indices[e][1]
            packages[m][p] = packages[m][p] + 1
         
         k = 0
         for m in range(self.inst.nM):
            for p in range(len(self.inst.Rms[m])):
               if packages[m][p] > 0 : 
                  lsPhase31[k] = self.mdl.add_constraint(self.mdl.sum(self.tb[m,p]) \
                  >=  packages[m][p], ctname=f'ls31_{v}')
                  k = k + 1

         sol3 = self.mdl.solve()

         for e in range(len(lsPhase30)):   # release solution
            self.mdl.remove_constraint(lsPhase30[e])

         for e in range(len(lsPhase31)):
            self.mdl.remove_constraint(lsPhase31[e])

         print("Local Search Phase 3: ",sol3.objective_value)

       # update solution
      solu.reset()
      for d in range(self.inst.nNodes):
         for v in self.inst.Vd[d]:
            for f in self.inst.flowsNode[d]:
               if self.y[d,v,f].solution_value >= 0.5:
                  solu.flowCap[f] = solu.flowCap[f] - self.inst.sV[v]
                  solu.flowD[d][v] = f
                  solu.collectedItems[v] = True

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

#      Rms ={}
#      for m in range(self.inst.nM):
#         Rms[m] = [0] * len(self.inst.Rms[m])
#         for p in range(len(self.inst.Rms[m])):
#            
#            for v in self.inst.Rms[m][p]:
#               if not solu.collectedItems[v] : 
#                  Rms[m][p] = Rms[m][p] + 1
#            
#            for d in range(self.inst.nNodes):
#               if self.inst.dmp[d][m][p]:
#                  if sol1.get_value(self.sb[m,d,p])<= 0.5 :
#                     if len(self.inst.Rms[m][p]) > 2 and Rms[m][p] >= len(self.inst.Rms[m][p])-1:
#                        self.sb[m,d,p].ub = 0
#                  else:      
#                        self.sb[m,d,p].lb = 1 
#

