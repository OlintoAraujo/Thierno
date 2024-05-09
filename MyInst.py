import sys
import os
import random
import networkx as nx
from collections import defaultdict
from random import randint
from more_itertools import powerset


seed = 2023
random.seed(seed)

#r,s, ms = spatial_dependency_H(nV,nM,20)

def spatial_dependency_H(nV,nM,T):
    # adding monitoring application requirements
    V = list(range(nV))
    l = int(nV / nM) #length of the monitoring application
    s_r_m = [V[i * l:(i + 1) * l] for i in range((nV + l - 1) // l )]
    # setting monitoring requirement for each monitoring application
    R_m = {}
    for m in range(nM):
        R_m[m] = s_r_m[m]
    # getting the spatial dependencies
    Rs = {}
    for m in range(nM):
        Rs[m] = [list(x) for x in powerset(R_m[m]) if x]

    # list of spatial
    Rms = {}
    for k,v in Rs.items():
        Rms[k] = {i: sublist for i, sublist in enumerate(v)}

    #list of temporal
    Rmt = {}
    for k,v in Rs.items():
        Rms[k] = {i: random.randint(T/2, 2*T) for i, sublist in enumerate(v)}
    return R_m, Rs, Rms, Rmt
    



class NetworkGenerator:
    def __init__(self, nNodes: int, nFlows: int, maxL: int, nV: int, nM: int, min_size: int, max_size: int):
        
        self.maxL = maxL
        # generate the network infrastructure
        G = nx.barabasi_albert_graph(nNodes, 2)

        # arcs of the network
        arcs = list(G.edges)
        arcs2way = []
        for (i,j) in arcs:
           arcs2way.append((j,i))
        arcs.extend(arcs2way) 
        for i in range(nNodes):   # add in arcs the fake node
           arcs.append((i,nNodes))
  
        self.arcs = arcs
        
        # generate size of telemetry items between 2 and 8
        sV = [random.randint(min_size,max_size) for _ in range(nV)]
        #sV = {}
        #for v in range(nV):
        #    sV[v] = random.randint(min_capacity,max_capacity)
            
        # generate a subset of telemetry items for each device
        Vd = {}
        for d in range(nNodes):
            Vd[d] = random.sample(range(nV), random.randint(1, nV))
            Vd[d].sort(reverse=False)

        isVd ={} # is item v provided by d ?  T or F
        for d in range(nNodes):
            isVd[d] = [False] * nV 
            for v in Vd[d]:
                isVd[d][v] = True 

        # setting up temporal and spatial dependencies

        # Time limit
        T = 100

        # adding monitoring application requirements
        V = list(range(nV))
        l = int(nV / nM) #length of the monitoring application
        s_r_m = [V[i * l:(i + 1) * l] for i in range((nV + l - 1) // l )]
        # setting monitoring requirement for each monitoring application
        R_m = {}
        for m in range(nM):
            R_m[m] = s_r_m[m]
        # getting the spatial dependencies
        Rs = {}
        for m in range(nM):
            Rs[m] = [list(x) for x in powerset(R_m[m]) if x]

        # list of spatial
        Rms = {}
        for k,v in Rs.items():
            Rms[k] = {i: sublist for i, sublist in enumerate(v)}

        #list of temporal
        Rmt = {}
        for k,v in Rs.items():
            Rmt[k] = {i: random.randint(T/2, 2*T) for i, sublist in enumerate(v)}

        #print("RrrrrrrrrrrrrrrrrrrrrrrrMs : ", Rms)
        #print(" ")
        #print("Rrrrrrrrrrrrrrrrrmmmmmt : ", Rmt)
            
        #exit(1)
        dmp ={}  # True if device d gives the package P to application m
        for d in range(nNodes):
            dmp[d] = {}
            for m in range(nM):
                dmp[d][m] = []  
                for p in range(len(Rms[m])): 
                   ok = True
                   #for v in Rms[m][p]:
                   for v in range(len(Rms[m][p])):  
                      if not(Rms[m][p][v] in Vd[d]): 
                         ok = False
                         break
                   dmp[d][m].append(ok)

        # Generate F flows
        flows_infos = {}
        for f in range(nFlows):
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
        D_f = [destination[1] for destination in flows_infos.values()]
        flowCap = [capacity[2] for capacity in flows_infos.values()]
                
        # getting the shortest path for each flow
        flows = {}
        for f in range(nFlows):
            s = S_f[f]
            d = D_f[f]
            flows[f] = nx.shortest_path(G, s, d)

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
        self.flowCap = flowCap
        self.flowsNode = flowsNode
        self.Vd = Vd
        self.isVd = isVd
        self.dmp = dmp
        self.maxL = maxL
        self.arcs = arcs

    # printing the instances
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
    inst.printI()
    

    # Create a folder to store the instances if it does not exist
    Path_To_Save_Instances = "./instances/my_instances/" + str(nNodes) + "_" +str(maxL) + "/"
    if not os.path.exists(Path_To_Save_Instances):
        os.makedirs(Path_To_Save_Instances)

    inst.save_to_file(Path_To_Save_Instances + "/" + "H_instance_" + str(nNodes) + "_" + str(nFlows) + "_"\
    +str(maxL)+"_"+ str(nV) + "_" + str(nM)+"_"+str(min_size)+"_"+str(max_size) )