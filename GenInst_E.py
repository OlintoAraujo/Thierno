from docplex.mp.model import Model
import sys
import os
import random
import networkx as nx
from collections import defaultdict
from random import randint
from itertools import chain, combinations, permutations


#seed = 2023
#random.seed(seed)
#seed = random.seed()
random.seed()



def spatial_dependency_E(nV,T):
    list_items = list(range(nV))
    num_spatials = random.randint(2,nV/2)
    spatials_max_length = random.randint(2,8)
    spatials = []
    remaining_spatials = list_items.copy()
    for _ in range(num_spatials):
        spatial_length = random.randint(2, spatials_max_length)
        spatial = random.sample(remaining_spatials, spatial_length)
        if spatial not in spatials:
            spatials.append(spatial)
    #print(spatials)
    spatials_dict = {}
    temporals_dict = {}
    for l in range(len(spatials)):
        spatials_dict[l] = spatials[l]
        temporals_dict[l] = random.randint(T/2, (T+T/2))
    #print(spatials_dict)
    dependencies = [spatials_dict, temporals_dict]
    return dependencies

def spatial_dependency_H(nV,nM,T):
    list_items = list(range(nV))
    num_spatials = random.randint(2,nV/2)
    #spatials_max_length = random.randint(2,nV/2)
    spatials_max_length = int(nV/nM)
    spatials = []
    remaining_spatials = list_items.copy()
    for _ in range(num_spatials):
        if not remaining_spatials:
            break
        #spatial_length = random.randint(2, spatials_max_length)
        spatial_length = int(nV/nM)
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
    def __init__(self, nNodes: int, nFlows: int, maxL: int, nV: int, nM: int, min_size: int, max_size: int):
        
        self.nNodes = nNodes
        self.maxL = maxL
        # generate the network infrastructure
        G = nx.barabasi_albert_graph(nNodes, 3)
        
        # arcs of the network
        arcs = list(G.edges)
        arcs2way = []
        for (i,j) in arcs:
           arcs2way.append((j,i))
        arcs.extend(arcs2way) 
        for i in range(nNodes):   # add in arcs the fake node
           arcs.append((i,nNodes))
  
        self.arcs = arcs

       # generate size of telemetry items 
        sV = [random.randint(min_size,max_size) for _ in range(nV)]
        #sV = {}
        #for v in range(nV):
        #    sV[v] = random.randint(min_capacity,max_capacity)
            
        # generate a subset of telemetry items for each device
        Vd = {}
        for d in range(nNodes):
            #Vd[d] = random.sample(range(nV), random.randint(2,int(nV/2)))
            Vd[d] = random.sample(range(nV), random.randint(2,nV))
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
            dependencies = spatial_dependency_E(nV,T)
            #Rms[m] = spatial_dependency(nV,T)
            Rms[m] = dependencies[0]
            Rmt[m] = dependencies[1]

        #print("RrrrrrrrrrrrrrrrMs : ", Rms)
        #exit(1)
            
        
#        dmp ={}  # True if device d gives the package P to application m
#        for d in range(nNodes):
#            dmp[d] = {}
#            for m in range(nM):
#                dmp[d][m] = []  
#                for p in range(len(Rms[m])): 
#                   ok = True
#                   for v in range(len(Rms[m][p])):  
#                      if not(Rms[m][p][v] in Vd[d]): 
#                         ok = False
#                         break
#                   dmp[d][m].append(ok) 


        # calculating the flows 
        flows = {}
        flowCap= []
        self.buildModel()
        for f in range(nFlows):
            s = random.randint(0, nNodes-1)
            flows[f] = self.calcPath(s)
            flowCap.append(random.randint(min_size, 2*max_size))
        
        # getting the flows crossing each device
        flowsNode = defaultdict(list)
        for d in range(nNodes):
            for f in range(nFlows) :
                if d in flows[f]:
                    flowsNode[d].append(f)

        #define the parameters
        self.nNodes = nNodes
        self.nFlows = nFlows
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
#        self.S_f = S_f
#        self.E_f = E_f
        self.flowCap = flowCap 
#        self.GF = GF
        self.maxL = maxL
        self.flowsNode = flowsNode
        self.Vd = Vd
        self.isVd = isVd
#        self.dmp = dmp
        self.arcs = arcs
        
    def calcPath(self,s : int):
       self.z[s].set_lb(1)
       
       sol = self.mdl.solve()
       if not sol:
         print("No feasible solution")
         exit(1)
       ss = s
       path = [ss]
       while ss != self.nNodes:
          for (i,j) in self.arcs: 
             if (i != ss): 
                continue
             if sol.get_value(self.x[i,j]) > 0.5: 
                path.append(j)
                ss = j
                break
    
       self.mdl.add_constraint(self.mdl.sum(self.x[path[i],path[i+1]] for i in range(len(path)-1)) <= self.maxL) 
       self.z[s].set_lb(0)
       #self.mdl.export_as_lp('tsp.lp')
       return path[0 : len(path)-1]

    def buildModel(self):
       
       # Define model
       self.mdl = Model('PathModel')

      # Parameters
       bigM = self.nNodes * 2  # Assuming n is defined
       
       # Variables
       self.x = {(i, j): self.mdl.integer_var(name='x_{}_{}'.format(i, j))
            for (i, j) in self.arcs}
       
       self.u = {i : self.mdl.continuous_var(name='u_{}'.format(i), lb = 0, ub = bigM ) \
       for i in range(self.nNodes+1)}
       
       self.z = {i : self.mdl.integer_var(name='z_{}'.format(i), lb = 0, ub = 1 ) \
       for i in range(self.nNodes+1)}
       # Objective function
       self.mdl.minimize(self.mdl.sum(self.x[i, j] for (i, j) in self.arcs))
    
       # Constraints
       self.mdl.add_constraint(self.mdl.sum(self.x[i,j] for (i,j) in self.arcs if j == self.nNodes ) == 1, \
       ctname='end')
      
       for ii in range(nNodes):
          self.mdl.add_constraint(self.mdl.sum(self.x[i,j] for (i,j) in self.arcs if i == ii) <= 1, \
          ctname=f'suc{ii}')
       
       for jj in range(self.nNodes): 
          self.mdl.add_constraint(self.mdl.sum(self.x[i, j] for (i, j) in self.arcs if j == jj ) -\
          self.mdl.sum(self.x[j,i] for (j,i) in self.arcs if j == jj )  == -self.z[jj], ctname='b_{}'.format(jj))
    
       for (ii,jj) in self.arcs:
          self.mdl.add_constraint( self.mdl.sum(self.u[j] for j in range(self.nNodes+1) if j == jj) >= \
          self.mdl.sum(self.u[i] + 1 + bigM * (self.x[i,j] - self.z[j] - 1) \
          for (i,j) in self.arcs if j == jj and i == ii) , ctname=f'cycle{ii,jj}') 
    
       self.mdl.add_constraint(self.mdl.sum(self.x[i, j] for (i, j) in self.arcs ) == self.maxL+1,\
       ctname='length')
       
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
            
            # maximum_length 
            f.write(str(self.maxL)+'\n')

            self.arcs = [tupla for tupla in self.arcs if tupla[1] != self.nNodes]
            # nro of arcs
            f.write(str(len(self.arcs)) + '\n')

            # write arcs of the network
            for arc in self.arcs:
                f.write(f"{arc[0]} {arc[1]}\n")


if __name__ == "__main__":

    nNodes = int(sys.argv[1])
    nFlows = int(sys.argv[2])
    maxL = int(sys.argv[3])
    nV = int(sys.argv[4])
    nM = int(sys.argv[5])
    min_size= int(sys.argv[6])
    max_size= int(sys.argv[7])
    
    inst = NetworkGenerator(nNodes, nFlows, maxL, nV, nM, min_size, max_size)
    #inst.printI()
    

    # Create a folder to store the instances if it does not exist
    Path_To_Save_Instances = "./instances/"  
    if not os.path.exists(Path_To_Save_Instances):
        os.makedirs(Path_To_Save_Instances)

    #inst.save_to_file(Path_To_Save_Instances + "/" + "E_instance_" + str(nNodes) + "_" + str(nFlows) + "_"\
    #+str(maxL)+"_"+ str(nV) + "_" + str(nM)+"_"+str(min_size) + "_" + str(max_size) )


    counter = 1

    # Set the base file name
    base_filename = "E_instance_" + str(nNodes) + "_" + str(nFlows) + "_"\
    +str(maxL)+"_"+ str(nV) + "_" + str(nM)+"_"+str(min_size) + "_" + str(max_size) + "_"

    # Set the file extension
    #file_extension = ".txt"

    # Loop until a unique file name is found
    while True:
        # Generate the file name with the current counter value
        filename = base_filename + str(counter) #+ file_extension

        # Generate the full file path
        file_path = os.path.join(Path_To_Save_Instances, filename)

        # Check if a file with the same name already exists
        if not os.path.exists(file_path):
            # If not, break the loop
            break

        # If a file with the same name already exists, increment the counter
        counter += 1

    # Save the instance to the file
    inst.save_to_file(file_path)
