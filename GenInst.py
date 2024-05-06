from docplex.mp.model import Model
import sys
import os
import random
import networkx as nx
from collections import defaultdict
from random import randint


seed = 2023
random.seed(seed)

def TSP(s : int , L: int,nNodes:int, arcs:list):
   
   # Define model
   mdl = Model('PathModel')
   
   for i in range(nNodes):   # arcs to the fake node
      arcs.append((i,nNodes))

   # Parameters
   bigM = nNodes * 2  # Assuming n is defined
   
   # Variables
   x = {(i, j): mdl.integer_var(name='x_{}_{}'.format(i, j))
        for (i, j) in arcs}
   
   u = {i : mdl.continuous_var(name='u_{}'.format(i), lb = 0, ub = bigM*(i != s) ) for i in range(nNodes+1)}
   # Objective function
   mdl.minimize(mdl.sum(x[i, j] for (i, j) in arcs))

   mdl.add_constraint(mdl.sum(x[i,j] for (i,j) in arcs if i == s ) == 1, ctname='start')
   mdl.add_constraint(mdl.sum(x[i,j] for (i,j) in arcs if j == nNodes ) == 1, ctname='end')
  
   # Constraints
   for jj in range(nNodes):
      mdl.add_constraint(mdl.sum(x[i,j] for (i,j) in arcs if j == jj) <= 1, ctname=f'suc{jj}')
   
   for jj in range(nNodes):
      mdl.add_constraint(mdl.sum(x[i,j] for (i,j) in arcs if j == jj) <= 1, ctname=f'suc{jj}')
  
   for jj in range(nNodes): 
      if  jj == s:
         continue 
      mdl.add_constraint(mdl.sum(x[i, j] for (i, j) in arcs if j == jj ) -\
      mdl.sum(x[j,i] for (j,i) in arcs if j == jj )  == 0, ctname='b_{}'.format(jj))

   for (ii,jj) in arcs:
      if  jj == s : 
         continue
      mdl.add_constraint( mdl.sum(u[j] for j in range(nNodes+1) if j == jj) >= \
      mdl.sum(u[i] + 1 + bigM * (x[i,j] - 1) for (i,j) in arcs if j == jj and i == ii) , ctname=f'cycle{ii,jj}') 

   mdl.add_constraint(mdl.sum(x[i, j] for (i, j) in arcs ) == L+1, ctname='length')
   
   mdl.export_as_lp("tsp.lp")
   
#   sol = mdl.solve()
#   path = [s]
#   while s != d:
#      for (i,j) in arcs: 
#         if (i != s): 
#            continue
#         if sol.get_value(x[i,j]) > 0.5: 
#            path.append(j)
#            s = j
#            break
#
#   return path

def spatial_dependency(nV,nM,T):
    list_items = list(range(nV))
    num_spatials = random.randint(2,nV/2)
    spatials_max_length = random.randint(2,4)
    #spatials_max_length = int(nV/nM)
    spatials = []
    remaining_spatials = list_items.copy()
    for _ in range(num_spatials):
        if not remaining_spatials:
            break
        spatial_length = random.randint(2, spatials_max_length)
        #spatial_length = int(nV/nM)
        spatial_length = min(spatial_length, len(remaining_spatials))
        spatial = random.sample(remaining_spatials, spatial_length)
        spatials.append(spatial)
        remaining_spatials = [elem for elem in remaining_spatials if elem not in spatial]
    #print(spatials)
    spatials_dict = {}
    temporals_dict = {}
    for l in range(len(spatials)):
        spatials_dict[l] = spatials[l]
        temporals_dict[l] = random.randint(T/2, 2*T)
    #print(spatials_dict)
    dependencies = [spatials_dict, temporals_dict]
    return dependencies



class NetworkGenerator:
    def __init__(self, nNodes: int, nFlows: int, pFlows: int, maxL: int, nV: int, nM: int, min_size: int, max_size: int):
        
        # generate the network infrastructure
        G = nx.barabasi_albert_graph(nNodes, 2)

        # arcs of the network
        arcs = list(G.edges)
        arcs2way = []
        for (i,j) in arcs:
           arcs2way.append((j,i))
        arcs.extend(arcs2way) 
        
        # generate size of telemetry items 
        sV = [random.randint(min_size,max_size) for _ in range(nV)]
        #sV = {}
        #for v in range(nV):
        #    sV[v] = random.randint(min_capacity,max_capacity)
            
        # generate a subset of telemetry items for each device
        Vd = {}
        for d in range(nNodes):
            Vd[d] = random.sample(range(nV), random.randint(2, nV))
            Vd[d].sort(reverse=False)

        isVd ={} # is item v provided by d ?  T or F
        for d in range(nNodes):
            isVd[d] = [False] * nV 
            for v in Vd[d]:
                isVd[d][v] = True 

        # setting up temporal and spatial dependencies
        T = 100
        
        Rms = {}
        Rmt = {}
        for m in range(nM):
            dependencies = spatial_dependency(nV,nM,T)
            #Rms[m] = spatial_dependency(nV,T)
            Rms[m] = dependencies[0]
            Rmt[m] = dependencies[1]
            
        
        dmp ={}  # True if device d gives the package P to application m
        for d in range(nNodes):
            dmp[d] = {}
            for m in range(nM):
                dmp[d][m] = []  
                for p in range(len(Rms[m])): 
                   ok = True
                   for v in range(len(Rms[m][p])):  
                      if not(Rms[m][p][v] in Vd[d]): 
                         ok = False
                         break
                   dmp[d][m].append(ok) 


        # Generate F flows
        # set of given flows
        GF = [i for i in range(int((pFlows * nFlows / 100)))] # set of given flows
        flows_infos = {}
        for f in range(nFlows) :
        #for f in list(set(range(nFlows)) - set(GF)):
            # Choose a random source and destination
            source = random.randint(0, nNodes-1)
            destination = random.randint(0, nNodes-1)
            # Make sure the source and destination are not the same
            while source == destination:
                destination = random.randint(0, nNodes-1)
            # Choose a random capacity for the flow
            capacity = random.randint(2*min_size, 2*max_size)
            #capacity = random.randrange(2,20, 2) # to compare 2 to 20
            # Add the flow to the dictionary
            flows_infos[f] = [source, destination, capacity]

        # getting the source, destination and capacity of each flow
        S_f = [source[0] for source in flows_infos.values()]
        E_f = [destination[1] for destination in flows_infos.values()]
        flowCap = [capacity[2] for capacity in flows_infos.values()]
                
        # getting the shortest path for each flow
        flows = {}
        for f in range(nFlows):
            s = S_f[f]
            d = E_f[f]
            #flows[f] = nx.shortest_path(G, s,  d)
            Nodes = [ 3, 4, 8]
            TSP(s,3,nNodes,arcs)
            #flows[f] = TSP(s,3,nNodes,arcs)
            #print(flows[f])
            print("source:",s," destination:",d)
            exit(1)

        # getting the flows crossing each device
        flowsNode = defaultdict(list)
        for d in range(nNodes):
            for f in range(nFlows) :
                if d in flows[f]:
                    flowsNode[d].append(f)




        #define the parameters
        self.nNodes = nNodes
        self.nFlows = nFlows
        self.pFlows = pFlows
        self.nV = nV
        self.nM = nM
        self.min_size = min_size
        self.max_size = max_size
        self.Vd = Vd
        self.sV = sV
        self.Rms = Rms
        self.Rmt = Rmt
        self.T = T
        self.flows = flows
        self.S_f = S_f
        self.E_f = E_f
        self.flowCap = flowCap
        self.GF = GF
        self.maxL = maxL
        self.flowsNode = flowsNode
        self.Vd = Vd
        self.isVd = isVd
        self.dmp = dmp
        self.arcs = arcs
        


    def printI(self):
       print("Number of nodes: ",self.nNodes,"\n")
       print("Flows: ",self.nFlows)
       print("Flow capacity: ",self.flowCap)
       for f in range(self.nFlows): 
          print("Flow ",f,self.flows[f])
       print("\nNumber of Items: ",self.nV)
       print("Items size: ",self.sV)
       print("\nNumber of applications: ",self.nM)
       print("Rms : ")
       for m in range(self.nM): 
          print("Application",m,self.Rms[m])  

       print("Rmt :")
       for m in range(self.nM): 
          print("Application",m,self.Rmt[m])  

       print("\nVd :")
       for d in range(self.nNodes): 
          print("Node",d,self.Vd[d])  
       
       for d in range(self.nNodes): 
          print("Paths crossing node",d,":",self.flowsNode[d])

    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            # nNodes
            f.write(str(self.nNodes) + '\n')

            # nFlows
            f.write(str(self.nFlows) + '\n')

            # flows capacities
            f.write(' '.join(map(str, self.flowCap)) + '\n')

            # flows paths
            for flow , path in self.flows.items():
                f.write(str(flow) + ' ' + ' '.join(map(str, path)) + '\n')

            # nV
            f.write(str(self.nV) + '\n')

            # sV
            f.write(' '.join(map(str, self.sV)) + '\n')

            # nM
            f.write(str(self.nM) + '\n')

            # spatial
            for m in range(self.nM):
                items = []
                for spav in self.Rms[m].values():
                    items.append(' '.join(map(str, spav)))
                f.write(str(m) + ' : ' + ' : '.join(items) + '\n')

            # time limit
            f.write(str(self.T) + '\n')

            # temporal
            for m in range(self.nM):
                times = []
                for tmpv in self.Rmt[m].values():
                    times.append(str(tmpv))
                f.write(str(m) + ' ' + ' '.join(times) + '\n')


            # Write Vd
            for d, v in self.Vd.items():
                f.write(str(d) + ' ' + ' '.join(map(str, v)) + '\n')

    def save_network(self,filename):
        with open(filename, 'w') as f:
            # flows to compute
            f.write(str(len(list(set(range(self.nFlows)) - set(self.GF)))) + '\n')
            # capacity of the flows
            for ff in list(set(range(self.nFlows)) - set(self.GF)):
                f.write(str(self.flowCap[ff]) + ' ')
            f.write('\n')
            # source and destination of the flows
            for ff in list(set(range(self.nFlows)) - set(self.GF)):
                f.write(f"{self.S_f[ff]} {self.E_f[ff]}\n")
            # value of maxL
            f.write(str(self.maxL) + '\n')
            # number of arcs in the network
            f.write(str(2*len(self.arcs)) + '\n')
            # write arcs of the network
            for arc in self.arcs:
                f.write(f"{arc[0]} {arc[1]}\n")



            


    


if __name__ == "__main__":

    nNodes = int(sys.argv[1])
    nFlows = int(sys.argv[2])
    pFlows = int(sys.argv[3])  # percentage of given flows. 
    maxL = int(sys.argv[4])
    nV = int(sys.argv[5])
    nM = int(sys.argv[6])
    min_size= int(sys.argv[7])
    max_size= int(sys.argv[8])
    
    inst = NetworkGenerator(nNodes, nFlows, pFlows, maxL, nV, nM, min_size, max_size)
    inst.printI()
    

    # Create a folder to store the instances if it does not exist
    Path_To_Save_Insatnces = "./instances/" + str(inst.nNodes) + "_" + str(inst.nFlows) + "_" + str(inst.nV) + "_" + str(inst.nM) +"_"+str(inst.min_size) + "_" + str(inst.max_size)
    if not os.path.exists(Path_To_Save_Insatnces):
        os.makedirs(Path_To_Save_Insatnces)

    inst.save_to_file(Path_To_Save_Insatnces + "/" + "instance_" + str(nNodes) + "_" + str(nFlows) + "_" + str(nV) + "_" + str(nM) )
    inst.save_network(Path_To_Save_Insatnces + "/" + "instance_network_" + str(nNodes) + "_" + str(nFlows) + "_" + str(pFlows) + "_" + str(maxL) + "_" + str(nV) + "_" + str(nM) )
    #print(inst.Rms)
    #print(inst.R_m)
    #print(inst.flowCap)
    #print(inst.flows)
    #print(inst.sV)
    print(inst.GF)

        
            
            
        
        
 
        
