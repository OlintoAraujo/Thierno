import sys
import os
import random
import networkx as nx
from collections import defaultdict
from random import randint


seed = 2023
random.seed(seed)




def spatial_dependency(nV,T):
    list_items = list(range(nV))
    num_spatials = random.randint(2,nV/2)
    spatials_max_length = random.randint(1,3)
    spatials = []
    remaining_spatials = list_items.copy()
    for _ in range(num_spatials):
        spatial_length = random.randint(1, spatials_max_length)
        spatial = random.sample(remaining_spatials, spatial_length)
        if spatial not in spatials:
            spatials.append(spatial)
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
    def __init__(self, nNodes: int, nFlows: int, pFlows: int, maxL: int, nV: int, nM: int, min_capacity: int, max_capacity: int):
        
        # generate the network infrastructure
        G = nx.barabasi_albert_graph(nNodes, 2)

        # arcs of the network
        arcs = list(G.edges)
        
        # generate size of telemetry items between 2 and 8
        sV = [random.randint(min_capacity,max_capacity) for _ in range(nV)]
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
        T = 100
        
        Rms = {}
        Rmt = {}
        for m in range(nM):
            dependencies = spatial_dependency(nV,T)
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
            capacity = random.randint(min_capacity, 2*max_capacity)
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
        self.pFlows = pFlows
        self.nV = nV
        self.nM = nM
        self.min_capacity = min_capacity
        self.max_capacity = max_capacity
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
                f.write(f"{arc[1]} {arc[0]}\n")



            


    


if __name__ == "__main__":
    nNodes = int(sys.argv[1])
    nFlows = int(sys.argv[2])
    pFlows = int(sys.argv[3])
    maxL = int(sys.argv[4])
    nV = int(sys.argv[5])
    nM = int(sys.argv[6])
    min_capacity = int(sys.argv[7])
    max_capacity = int(sys.argv[8])
    inst = NetworkGenerator(nNodes, nFlows, pFlows, maxL, nV, nM, min_capacity, max_capacity)
    inst.printI()
    

    # Create a folder to store the instances if it does not exist
    Path_To_Save_Insatnces = "./Instances/" + str(inst.nNodes) + "_" + str(inst.nFlows) + "_" + str(inst.nV) + "_" + str(inst.nM) + str(inst.min_capacity) + "_" + str(inst.max_capacity)
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

        
            
            
        
        
 
        
