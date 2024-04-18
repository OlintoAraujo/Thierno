from docplex.mp.model import Model
import numpy as np
import time
from Instance import *


class Model:
    
    def __init__(self):
#        start_total = time.time()
        
        # build model ##########################################################################
        mdl = Model()
        start = time.time()      
        s = modelo.integer_var_dict(keys1=A, keys2=B, keys3=C, keys4=D, name="s")

        modl.add_constraint(modelo.sum(variaveis[a, b, c, d] for a in A for b in B for c in C for d in D) <= 100)

        print("time_var:", time.time() - start)
        mdl.minimize(sum(i * w[i] for i in [(i) for i in V if i >= self.sol.lb]))

        start = time.time()
        mdl.add_constraint(sum(w[i] for i in [(i) for i in V if i >= self.sol.lb]) == 1)
        
        for k in range(1, lenV):
            # scheduling arcs
            x_i_sum = sum(x[i, j] for (i, j) in Al if i == V[k])
            x_j_sum = sum(x[i, j] for (i, j) in Al if j == V[k])

            # connecting arcs
            y_j = y[V[k - 1], V[k]]
            y_i = y[V[k], V[k + 1]] if k < lenV - 1 else 0 

            # injection flow
            w_expr = self.sol.inst.m * w[V[k]] if V[k] >= self.sol.lb else 0 

            mdl.add_constraint(-x_i_sum + x_j_sum + y_j - y_i  == w_expr)  
            
        time_model = time.time() - start
        print("time_const1:", time_model)
        start = time.time()
        for (k, n) in pl.items():
            mdl.add_constraint(sum(x[i, j] for (i, j) in Al if j - i == k) == n)
        ct = time.time() - start
        print("time_const2:", ct)
        print("time_const_total:", time_model + ct)
        self.time_arc = time_arc
        self.time_model = time_model
        self.mdl =  mdl
        print(f"time_total: {time.time() - start_total}")

    def export_lp(self, filename: str):
        self.mdl.export_as_lp(filename)
