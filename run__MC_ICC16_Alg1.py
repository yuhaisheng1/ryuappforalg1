'''
Created on 2016-1-3

@author: Administator
'''
from __MC_ICC16_Alg1 import  MC_ICC16_Alg
class Run___MC_ICC16_Alg():
   def __init__(self,*args):	
	self.arg = args[0]
	self.debugfile = open("run_MC_ICC16_Alg1.txt",'w')  	
	self.debugfile.write("Run___MC_ICC16_Alg start\n")
	self.debugfile.flush()
    	self.PathSet_selected = {}
    	self.Paths_set = {}	
    	__mc_icc16_alg = MC_ICC16_Alg(self.arg)             
    	self.PathSet_selected = __mc_icc16_alg.PathSet_selected
	self.debugfile.write("instance MC_ICC16_Alg complete\n")
	self.debugfile.flush()
	
    	self.Paths_set = __mc_icc16_alg.Paths_set      
 	self.debugfile.write("Run___MC_ICC16_Alg end\n")
	self.debugfile.flush()
    
    
