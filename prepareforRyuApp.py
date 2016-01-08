'''
Created on 2016-1-3

@author: Administator
'''
from __MC_ICC16_Alg1 import  __MC_ICC16_Alg
if __name__ == '__main__':
    _linkinfodict = {}
    PathSet_selected = {}
    Paths_set = {}
    __mc_icc16_alg = __MC_ICC16_Alg()
    #mc_linkinfodict = __mc_icc16_alg._linkinfodict
    mc_PathSet_selected = __mc_icc16_alg.PathSet_selected
    mc_Paths_set = __mc_icc16_alg.Paths_set
    
    
    #f1 = open("_linkinfodict.txt",'w')
    f2 = open("PathSet_selected.txt",'w')
    f3 = open("Paths_set.txt",'w')
    
    #f1.write(str(mc_linkinfodict))
    f2.write(str(mc_PathSet_selected))
    f3.write(str(mc_Paths_set))
    #f1.close()
    f2.close()
    f3.close()
    print "file write done"
   
    
    