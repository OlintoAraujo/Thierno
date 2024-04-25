import sys
import random
import networkx as nx
from collections import defaultdict
from random import randint
from itertools import chain, combinations, permutations


seed = 2023
random.seed(seed)


import random

# def network_good (nNodes, nFlows):
#     # Generate a graph following the Barabasi model
#     m = 1
#     G = nx.barabasi_albert_graph(nNodes, m)

#     # Generate a list of all possible paths between each pair of nodes
#     all_paths = {(u, v): list(nx.all_simple_paths(G, u, v)) for u, v in itertools.permutations(G.nodes(), 2) if u != v}

#     # Initialize a list to keep track of which nodes have been crossed by a flow
#     nodes_crossed = [False] * nNodes

#     # Generate nFlows flows, ensuring that each node is crossed by at least one flow and that the length of the path of each flow is between 2 and nNodes/2
#     #nFlows = 10
#     flows = {}
#     for i in range(nFlows):
#         # Randomly select a source node and a destination node
#         source = random.choice(list(G.nodes()))
#         destination = random.choice(list(G.nodes()))
#         while source == destination or nodes_crossed[source] and nodes_crossed[destination]:
#             source = random.choice(list(G.nodes()))
#             destination = random.choice(list(G.nodes()))
#         # Select a random path between the source and destination nodes that meets the length criteria
#         possible_paths = [path for path in all_paths[(source, destination)] if 2 <= len(path) <= nNodes/2]
#         path = random.choice(possible_paths)
#         flows[i] = path
#         # Mark the nodes on the path as having been crossed by a flow
#         for node in path:
#             nodes_crossed[node] = True

#     # If any nodes have not been crossed by a flow, randomly select a flow and modify it to cross the node
#     for node in range(nNodes):
#         if not nodes_crossed[node]:
#             # Randomly select a flow to modify
#             flow_index = random.randint(0, nFlows-1)
#             flow_path = flows[flow_index]
#             # Randomly select a node on the flow path to replace with the uncrossed node
#             replace_index = random.randint(0, len(flow_path)-1)
#             flow_path[replace_index] = node
#             # Update the flow path in the dictionary
#             flows[flow_index] = flow_path
#             # Mark the node as having been crossed by a flow
#             nodes_crossed[node] = True

#     return flows

# def generate_network(nNodes,nFlows):
#     # generate the network infrastructure
#     G = nx.barabasi_albert_graph(nNodes, 2)
#     # get all possible path from each pairs
#     #all_paths = {(u, v): list(nx.all_simple_paths(G, u, v)) for u, v in itertools.permutations(G.nodes(), 2) if u != v}
#     # keep track of visited nodes
#     nodes_crossed = [False] * nNodes
#     # initialise the flows path
#     flows = {}
#     for f in range(nFlows):
#         # Randomly select a source node and a destination node
#         source = random.choice(list(G.nodes()))
#         destination = random.choice(list(G.nodes()))
#         while source == destination or nodes_crossed[source] and nodes_crossed[destination]:
#             source = random.choice(list(G.nodes()))
#             destination = random.choice(list(G.nodes()))
#         # Select a random path between the source and destination nodes that meets the length criteria
#         #possible_paths = [path for path in all_paths[(source, destination)] if 2 <= len(path) <= nNodes/2]
#         #path = random.choice(possible_paths)
#         path = nx.shortest_path(G, source, destination)
#         flows[f] = path
#         # Mark the nodes on the path as having been crossed by a flow
#         for node in path:
#             nodes_crossed[node] = True

#     for node in range(nNodes):
#         if not nodes_crossed[node]:
#             # Randomly select a flow to modify
#             flow_index = random.randint(0, nFlows-1)
#             flow_path = flows[flow_index]
#             # Randomly select a node on the flow path to replace with the uncrossed node
#             replace_index = random.randint(0, len(flow_path)-1)
#             flow_path[replace_index] = node
#             # Update the flow path in the dictionary
#             flows[flow_index] = flow_path
#             # Mark the node as having been crossed by a flow
#             nodes_crossed[node] = True

#     # getting the flows crossing each device
#         flowsNode = defaultdict(list)
#         for d in range(nNodes):
#             for f in range(nFlows) :
#                 if d in flows[f]:
#                     flowsNode[d].append(f)

#     return flows, flowsNode




def is_connected(flows, nNodes):
    # Create a set of visited nodes
    visited = set()

    # Start with the first node in the first flow
    start_node = flows[0][0]
    visited.add(start_node)

    # Perform a depth-first search (DFS) to visit all connected nodes
    stack = [start_node]
    while stack:
        node = stack.pop()
        for flow in flows.values():
            if node in flow:
                for next_node in flow:
                    if next_node not in visited:
                        visited.add(next_node)
                        stack.append(next_node)

    # Check if all nodes are visited
    return len(visited) == nNodes

def generate_network(nNodes, nFlows):
    # Create a dictionary to store the flows
    flows = {}

    # Assign one flow to each node
    listOfNodes  = list(range(nNodes))
    for i in range(nNodes):
        # Select a random path length between 2 and 5
        path_length = random.randint(2, 5)
        #path_length = random.randint(2, int(nNodes/4))

        # Generate a random path that includes the current node
        listOfNodes = random.shuffle(listOfNodes)
        path = [i]
        for _ in range(path_length - 1):
            next_node = random.randint(0, nNodes - 1)
            while next_node in path:
                next_node = random.randint(0, nNodes - 1)
            path.append(next_node)

        # Add the flow to the dictionary
        flows[i] = path

    # Assign the remaining flows randomly
    for i in range(nNodes, nFlows):
        # Select a random start node
        start_node = random.randint(0, nNodes - 1)

        # Select a random path length between 2 and nNodes/2
        path_length = random.randint(2, nNodes/2)

        # Generate a random path
        path = [start_node]
        for _ in range(path_length - 1):
            next_node = random.randint(0, nNodes - 1)
            while next_node in path:
                next_node = random.randint(0, nNodes - 1)
            path.append(next_node)

        # Validate the path
        if len(set(path)) != len(path):
            print(f"Error: Invalid path (duplicate nodes) for flow {i}")
            continue

        # Add the flow to the dictionary
        flows[i] = path

    # Check if the graph is connected
    if not is_connected(flows, nNodes):
        print("Error: The generated graph is not connected.")
        return None

    # getting the flows crossing each device
    flowsNode = defaultdict(list)
    for d in range(nNodes):
        for f in range(nFlows) :
            if d in flows[f]:
                flowsNode[d].append(f)

    return flows, flowsNode



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
    def __init__(self, nNodes: int, nFlows: int, nV: int, nM: int, min_capacity: int, max_capacity: int):
        
        # generate the network infrastructure
        flows, flowsNode = generate_network(nNodes, nFlows)

        # capacities of the flows
        flowCap = [random.randint(min_capacity,2*max_capacity) for _ in range(nFlows)]
        
        # generate size of telemetry items between 2 and 8
        sV = [random.randint(min_capacity,max_capacity) for _ in range(nV)]
        #sV = {}
        #for v in range(nV):
        #    sV[v] = random.randint(min_capacity,max_capacity)
            
        # generate a subset of telemetry items for each device
        Vd = {}
        for d in range(nNodes):
            Vd[d] = random.sample(range(nV), random.randint(3, nV))
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
            dependencies = spatial_dependency_H(nV,nM,T)
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

        #define the parameters
        self.nNodes = nNodes
        self.nFlows = nFlows
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
        self.flowCap = flowCap
        self.flowsNode = flowsNode
        self.Vd = Vd
        self.isVd = isVd
        self.dmp = dmp

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

if __name__ == "__main__":
    nNodes = int(sys.argv[1])
    nFlows = int(sys.argv[2])
    nV = int(sys.argv[3])
    nM = int(sys.argv[4])
    min_capacity = int(sys.argv[5])
    max_capacity = int(sys.argv[6])
    inst = NetworkGenerator(nNodes, nFlows, nV, nM, min_capacity, max_capacity)
    inst.printI()
    inst.save_to_file("hard_instance_" + str(nNodes) + "_" + str(nFlows) + "_" + str(nV) + "_" + str(nM))
