
class Instance:
    def __init__(self, sfile: str):
        
       self.flows:dict={}
       self.flowsNode={}
    # read data for instance file
       with open(sfile, 'r') as file:
          self.nNodes = int(file.readline())
          for i in range(self.nNodes):
             self.flowsNode[i] = []  

          self.nFlows = int(file.readline())
          line = file.readline().strip().split()
          self.flowCap =  [ int(i) for i in line[0:len(line)]  ]
           
          for n in range(self.nFlows): 
              line = file.readline().strip().split()
              flow = int(line[0])
              self.flows[flow] = [ int(i) for i in line[1:len(line)]  ]
              for i in range(len(self.flows[flow])):
                 node = self.flows[int(line[0])][i]
                 self.flowsNode[node].append(flow);

          for i in range(self.nNodes): # the start node of the flow can be the same as the end node
             self.flowsNode[i] = set(self.flowsNode[i])

          self.nV = int(file.readline())
          line = file.readline().strip().split()
          self.sV =  [ int(i) for i in line[0:len(line)]  ]
          self.nM = int(file.readline())
        
          self.Rms ={}
          for i in range(self.nM):
             self.Rms[i] = {}
             line = file.readline().strip().split()
             p = []
             np = 0
             for j in  range(2,len(line)):
                if line[j] != ':' : 
                   p.append(int(line[j]))
                if line[j] == ":" or j == len(line)-1 :    
                   self.Rms[i][np] = p
                   p = []  
                   np = np + 1 

            
          line = file.readline().strip().split()
          self.T = int(line[0])

          self.Rmt ={}
          for m in range(self.nM):
             line = file.readline().strip().split()
             self.Rmt[m] =[ int(i) for i in line[1:len(line)]  ]
 
          for m in range(self.nM):
             for i in range(len(self.Rmt[m])):
                if self.Rmt[m][i] > 0 :
                   if self.Rmt[m][i] > self.T : 
                      self.Rmt[m][i] = 0  # set P is outdated 
                   else:   
                      self.Rmt[m][i] = 1  

          self.Vd ={} 
          for i in range(self.nNodes):
             line = file.readline().strip().split()
             self.Vd[int(line[0])] = [ int(i) for i in line[1:len(line)]  ]

          self.dmp ={}
          for d in range(self.nNodes):
             self.dmp[d] = {}
             for m in range(self.nM):
                self.dmp[d][m] = []  
                for p in range(len(self.Rms[m])): 
                   ok = True
                   for v in range(len(self.Rms[m][p])):  
                      if not(self.Rms[m][p][v] in self.Vd[d]): 
                         ok = False
                         break
                   self.dmp[d][m].append(ok)   

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
 
