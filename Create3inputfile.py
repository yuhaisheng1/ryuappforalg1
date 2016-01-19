#coding=utf-8
'''
Created on 2015-12-20

@author: Guo Zhiqiang
'''


import random
from  GetAllPath import Node
from  GetAllPath import Path
from  GetAllPath import findPath
from  GetAllPath import getAllPath
from  GetAllPath import NodeGraph

class Ryutopoinfo:
    
    def __init__(self):
       self._linkinfodict = {}  ##所有结点对的link信息
       self.swlinkinfodict = {}  ##存储从文件中读取的swlink_to_port信息
       self._accesstable = {}	##存储从文件中读取的sw_port_to_host信息
       self._hostsnodes = []
       self._Mboxnodes = []             ##存储MiddleBox节点（mac标识）
       self._TDhosts = []               ##存储trafficdemand的host节点（mac标识）              
       self._nodes = []                  ##拓扑中所有的非孤立节点
       self._nodeslink = {}            ##以列表结构存储各个拓扑节点的邻接信息
       self.nodegraph = None            ##定义一个NodeGraph对象（相应的类在GetAllPath.py文件中定义）
       self._allclassnodes = []          ##存储了实例化所有节点的图
      
################################################################################################################################
       	       
       f1 = open("linktoportflie.txt",'r')

       f2 = open("accesshostflie.txt",'r')       

       str_linkinfodict = f1.read()

       str_accesstable = f2.read()
        
       f1.close()

       f2.close()      

       self.swlinkinfodict =eval(str_linkinfodict)

       self._accesstable = eval(str_accesstable)
       
       for key,val in self.swlinkinfodict.items():
           self._linkinfodict[str(key[0]),str(key[1])] = [str(val[0]),str(val[1])]
	   self._linkinfodict[str(key[1]),str(key[0])] = [str(val[1]),str(val[0])]
	   

       for key,val in self._accesstable.items():
           self._linkinfodict[str(key[0]),str(val)] = [str(key[1]),str(val)]
	   self._linkinfodict[str(val),str(key[0])] = [str(val),str(key[1])]
	   if val not in self._hostsnodes:
		self._hostsnodes.append(val)
       #print str(self._linkinfodict)
       for key in self._linkinfodict.keys():
	   #print str(key)
	   #print type(key)
	   #print key[1]
           if key[0] not in self._nodes:
		self._nodes.append(key[0])
	   if key[1] not in self._nodes:
		self._nodes.append(key[1])
           self._nodeslink.setdefault(key[0],[]).append(key[1])


##########################################################################################
       for toponode in self._nodes:           
           nodeclass = Node(self._nodeslink[toponode],toponode) ##实例化Node
           self._allclassnodes.append(nodeclass)  ##Node实例化对象的集合  

       self.nodegraph = NodeGraph(self._allclassnodes) ##实例化NodeGraph对象

       self.creatinputefile()
       self.create_linkinfodictfile()
#############################################################################################       

       
      
################################################################################################################################################
	
    def creatinputefile(self):      ##创建__MC_ICC16_Alg1.py的输入文件
        f1=open("_PathSet.txt","w")
        f2=open("_Cap_MBoxes.txt","w")       
        f3=open("_TrafficDemands.txt","w")
	f5=open("_Cap_links.txt","w")
        i=1
        randomnums = []
        while(i<=2):
            randomnum = random.randint(0, len(self._hostsnodes)-1)  ##从hostnodes中随机选择两个主机host作为MIiddleBox
            if randomnum not in randomnums:
                randomnums.append(randomnum)
                i = i+1
        for k in randomnums:
            self._Mboxnodes.append(self._hostsnodes[k])##随机生成的MiddleBox节点
        self._TDhosts = list(set(self._hostsnodes).difference(set(self._Mboxnodes))) ##所有的trafficdemand-host节点


        for i in self._Mboxnodes:    ##创建_Cap_MBoxes.txt文件
            str1 = "-nID_MBox"+"\t"+str(i)+"\t"+"-Cap"+"\t"+"200"+"\n"
            f2.write(str1)
	f2.flush()
        f2.close()
        
        ID_TDnum = 0                    ##创建_TrafficDemands.txt文件
        for j in self._TDhosts:            
            str2 = "-nID_TD"+"\t"+str(ID_TDnum)+"\t"+"-Src"+"\t"+j+"\t"+"-nRate"+"\t"+"100"+"\n"
            f3.write(str2)
            ID_TDnum = ID_TDnum + 1
	f3.flush()
        f3.close()  
        
        for i in self._Mboxnodes:    ##创建_PathSet.txt文件
            for j in self._TDhosts:                   
            #for j in self._switchesnodes:
                paths = getAllPath(j,i,self._allclassnodes,self.nodegraph)
                for path in paths:        
                    str4 = "-Dst"+"\t"+i+"\t"+"-Src"+"\t"+j+"\t"+"-pathLen"+"\t"+str(path.getpathlen())+"\t"+"-ReversePath"+"\t"+path.printpath()+"\n"
                    f1.write(str4)
	f1.flush()
        f1.close()

	for key in self._linkinfodict.keys():           ##创建_Cap_links.txt文件
            str3 = "Node_u"+"\t"+key[0]+"\t"+"-Node_v"+"\t"+key[1]+"\t"+"-Cap"+"\t"+"1000"+"\n"
            f5.write(str3)
	f5.flush()        
	f5.close()    
        
    def create_linkinfodictfile(self):
        f4 = open("_linkinfodict.txt",'w')
        f4.write(str(self._linkinfodict))
	f4.flush()
        f4.close()

