import sys
from Algoritm import *
from Instance import *
from Solution import *

if __name__ == "__main__":

    #  path instance file
     sfile = sys.argv[1]
    
     inst = Instance(sfile)
     inst.printI()

     solu = Solution(inst)
     print("\n\n")
     solu.printS()
# create instace Algoritmn 
#     alg = Algoritm(inst)


     #sum = alg.sum_values()
     
          
    #  SOLUTION ... continued for stored datas in instance solution
