	    model = Model('OINT')
	    
	    # Create decision variables
	    ##s_b = model.binary_var_dict({(m,d,P): 's_b_{}_{}_{}'.format(m,d,P) for m in inst.M for d in inst.D for P in range(len(inst.Rs[m]))})
	    s_b = {(m,d,P): model.binary_var(name='s_b_{}_{}_{}'.format(m,d,P)) for m in inst.M for d in inst.D for P in range(len(inst.Rs[m]))}
	    t_b = {(m,P): model.binary_var(name='t_b_{}_{}'.format(m,P)) for m in inst.M for P in range(len(inst.Rt[m]))}
	    ##t_b = model.binary_var_dict({(m,P): 't_b_{}_{}'.format(m,P) for m in inst.M for P in range(len(inst.Rt[m]))})
	    ##y = model.binary_var_dict({(d,v,f): 'y_{}_{}_{}'.format(d,v,f) for d in inst.D for v in inst.V for f in inst.F})
	    y = {(d,v,f): model.binary_var(name='y_{}_{}_{}'.format(d,v,f)) for d in inst.D for v in inst.V for f in inst.F}
	    ##x = model.binary_var_dict({(i,j,f): 'x_{}_{}_{}'.format(i,j,f) for i in inst.D for j in inst.D for f in inst.F if i != j})
	    x = {(i,j,f): model.binary_var(name='x_{}_{}_{}'.format(i,j,f)) for i in inst.D for j in inst.D for f in inst.F if i != j}
	    ##gg = model.continuous_var_dict({(i,f): 'gg_{}_{}'.format(i,f) for i in inst.D for f in inst.F})
	    gg = {(i,f): model.continuous_var(name='gg_{}_{}'.format(i,f)) for i in inst.D for f in inst.F}
	    ##s = model.integer_var_dict({(m,d,P): 's_{}_{}_{}'.format(m,d,P) for m in inst.M for d in inst.D for P in range(len(inst.Rs[m]))})
	    s = {(m,d,P): model.integer_var(name='s_{}_{}_{}'.format(m,d,P)) for m in inst.M for d in inst.D for P in range(len(inst.Rs[m]))}
	    ##t = model.integer_var_dict({(m,P): 't_{}_{}'.format(m,P) for m in inst.M for P in range(len(inst.Rt[m]))})
	    t = {(m,P): model.integer_var(name='t_{}_{}'.format(m,P)) for m in inst.M for P in range(len(inst.Rt[m]))}
	    
	    # constraints the flows to start from the source and end at the destination
	    for f in inst.FF:
	        model.add_constraint(model.sum(x[inst.S_f[f], j, f] for j in inst.D if inst.S_f[f]!=j) == 1 )
	        model.add_constraint(model.sum(x[i, inst.D_f[f], f] for i in inst.D if inst.D_f[f]!=i) == 1 )
	        
	    # Flow conservation constraints
	    for f in inst.FF:
	        for p in inst.D:
	            if p != inst.S_f[f] and p != inst.D_f[f]:
	                model.add_constraint(model.sum(x[i,p,f] for i in inst.D if p!=i) - model.sum(x[p,j,f] for j in inst.D if p!=j) == 0)
	    '''
	    # subtour elemination
	    subsets = [list(x) for x in powerset(inst.D) if x]            
	    for f in inst.FF:
	        for S in subsets:
	            if len(S) >= 2:
	                edges = [(i,j) for i in S for j in S if i != j]
	                expr = sum(x[i,j,f] for i,j in edges)
	                model.add_constraint(expr <= len(S) - 1)
        '''


	        
	    # removing cycle of size two
	    for i in inst.D:
	        for j in inst.D:
	            for f in inst.FF:
	                if i != j:
	                    model.add_constraint(x[i,j,f] + x[j,i,f] <= 1)
	                    
	    #MTZ 
	    for i in inst.D:
	        for j in inst.D:
	            for f in inst.F:
	                if i != j:
	                    model.add_constraint(gg[j,f] >= gg[i,f] + 1 - len(inst.D)*(1-x[i,j,f]))

	    
	    # limitting the route of flows
	    for f in inst.FF:
	        #model.add_constraint(model.sum(x[i, j, f] for i in inst.D for j in inst.D if i!=j) <= inst.max_route - 1)
	        model.add_constraint(model.sum(x[i, j, f] for i in inst.D for j in inst.D if i!=j) <= inst.max_route -1)
	        
	    # collected items are collected from device on the route of the flow
	    for d in inst.D:
	        for v in inst.V_d[d]:
	            for f in inst.FF:
	                model.add_constraint(y[d,v,f] <= model.sum(x[i,d,f] for i in inst.neighbors[d]))
	                
	    # a single telemetry item should be a collected by a single flow
	    for d in inst.D:
	        for v in inst.V_d[d]:
	            model.add_constraint(model.sum(y[d, v, f] for f in inst.F) <=1)
	    
	    # capacity of given flows should not be exceeded
	    for f in inst.GF:
	        model.add_constraint(model.sum(inst.Size[v] * y[d, v, f] for d in inst.shortest_path[f] for v in inst.V_d[d]) <=  inst.K_f[f])
	        model.add_constraint(model.sum(y[d,v,f] for d in [j for j in inst.D if j not in inst.shortest_path[f]] for v in inst.V_d[d] ) <= 0)
	        
	    # capacity
	    for f in inst.FF:
	        model.add_constraint(model.sum(inst.Size[v] * y[d, v, f] for d in inst.D for v in inst.V_d[d]) <=  inst.K_f[f])
	    
	    
	    # counting spatial dependencies
	    for m in inst.M:
	        for d in inst.D:
	            for P in range(len(inst.Rs[m])):
	                model.add_constraint(s[m,d,P] == model.sum(y[d, v, f] for v in inst.Rs[m][P] for f in inst.F))
	                
	    # counting temporal
	    for m in inst.M:
	        for P in range(len(inst.Rt[m])):
	            if inst.HH[P] > inst.TT[P]:
	                model.add_constraint(t[m,P] == model.sum(y[d, v, f] for d in inst.D for v in inst.Rs[m][P] for f in inst.F))
	                
	    # spatial dependencies
	    for m in inst.M:
	        for d in inst.D:
	            for P in range(len(inst.Rs[m])):
	                model.add_constraint(s_b[m,d,P] <= s[m,d,P]/len(inst.Rs[m][P]))
	                
	    # temporal dependencies
	    for m in inst.M:
	        for P in range(len(inst.Rt[m])):
	            model.add_constraint(t_b[m,P] <= t[m,P]/len(inst.Rt[m][P]))
	            
	    
	    # the objective function
	    obj_function = model.sum(s_b[m,d,P] for m in inst.M for d in inst.D for P in range(len(inst.Rs[m]))) + model.sum(t_b[m,P] for m in inst.M for P in range(len(inst.Rt[m])))
	    model.maximize(obj_function)
	    # creating class variables
	    self.inst = inst
	    self.model = model
	    self.s_b = s_b
	    self.t_b = t_b
	    self.s = s
	    self.t = t
	    self.x = x
	    self.y = y