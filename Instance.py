
class Instance:
    def __init__(self, sfile: str):
        
       self.Df:dict={}
       self.flowsNode={}
    # read data for instance file
       with open(sfile, 'r') as file:
          self.nNodes = int(file.readline())
          for i in range(self.nNodes):
             self.flowsNode[i] = []  

          self.nFlows = int(file.readline())
          line = file.readline().strip().split()
          self.capF =  [ int(i) for i in line[0:len(line)]  ]
           
          for n in range(self.nFlows): 
              line = file.readline().strip().split()
              flow = int(line[0])-1
              self.Df[flow] = [ int(i) for i in line[1:len(line)]  ]
              for i in range(len(self.Df[flow])):
                 node = self.Df[int(line[0])-1][i]
                 self.flowsNode[node-1].append(flow);

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

          self.Rmt ={}
          for i in range(self.nM):
             self.Rmt[i] = {}
             line = file.readline().strip().split()
             p = []
             np = 0
             for j in  range(2,len(line)):
                if line[j] != ':' : 
                   p.append(int(line[j]))
                if line[j] == ":" or j == len(line)-1 :    
                   self.Rmt[i][np] = p
                   p = []  
                   np = np + 1 
          
          self.Vd ={} 
          for i in range(self.nNodes):
             line = file.readline().strip().split()
             self.Vd[int(line[0])-1] = [ int(i) for i in line[1:len(line)]  ]
 
          
    def printI(self):
       print("Number of nodes: ",self.nNodes,"\n")
       print("Flows: ",self.nFlows)
       print("Flow capacity: ",self.capF)
       for i in range(self.nFlows): 
          print("Flow ",i+1,self.Df[i])
       print("\nNumber of Items: ",self.nV)
       print("Items size: ",self.sV)
       print("\nNumber of applications: ",self.nM)
       print("Rms : ")
       for i in range(self.nM): 
          print("Application",i,self.Rms[i])  

       print("Rmt :")
       for i in range(self.nM): 
          print("Application",i,self.Rmt[i])  

       print("\nVd :")
       for i in range(self.nNodes): 
          print("Node",i,self.Vd[i])  

