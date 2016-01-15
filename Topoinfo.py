#coding=utf-8
'''
Created on 2015-12-20

@author: Guo Zhiqiang
'''

import httplib    
import json
import random
from  GetAllPath import Node
from  GetAllPath import Path
from  GetAllPath import findPath
from  GetAllPath import getAllPath
from  GetAllPath import NodeGraph

class Ryuinfo:
    
    def __init__(self):
       self._links='/v1.0/topology/links'    ##ryu中获取switches、hostes、links等拓扑信息的restapi接口
       self._switches='/v1.0/topology/switches'
       self._hosts='/v1.0/topology/hosts'
       self._linkinfodict = {}          ##[srcpid,dstpid]=[src.portnum,dst.portnum]
       self._linksinfodict = {}           ##the list for all links' information
       self._hostsinfodict = {}           ##the list for all hosts-to-switches information
       self._host_to_switchinfo = {}      ##the  dict for hosts-to-switch information
       self._switchesinfo = {}            ##访问switches接口返回的switches信息
       self._switchportsinfo = {}       ##存储各个switch所对应的所有port_no
       self._hostsnodes = []            ##存储hosts节点（mac地址）
       self._Mboxnodes = []             ##存储MiddleBox节点（mac标识）
       self._TDhosts = []               ##存储trafficdemand的host节点（mac标识）
       self._switchesnodes = []         ##存储switches节点（dpid）
       self._nodes = []                  ##拓扑中所有的非孤立节点
       self._nodeslink = {}            ##以列表结构存储各个拓扑节点的邻接信息
       self.nodegraph = None            ##定义一个NodeGraph对象（相应的类在GetAllPath.py文件中定义）
       self._allclassnodes = []          ##存储了实例化所有节点的图
       self._webapiaddr = "192.168.26.133:8080"         ##ryu web访问地址及端口号
       self.getlinkinfo(self._webapiaddr)              
       self.gethostsinfo(self._webapiaddr)
       self.getswitchesinfo(self._webapiaddr)   
       for k in self._nodeslink:
         self._nodes.append(k)      ##从self._nodeslink中收集所有节点的信息（保证节点是非孤立节点）
       #for (k,v) in self._nodeslink.items():  
       #        print '%s:%s' %(k, v)   
       #print "\n"
       #for j in self._nodes:
       #    print j
       for toponode in self._nodes:           
           nodeclass = Node(self._nodeslink[toponode],toponode) ##实例化Node
           self._allclassnodes.append(nodeclass)  ##Node实例化对象的集合  
       self.nodegraph = NodeGraph(self._allclassnodes) ##实例化NodeGraph对象
       #for j in self._nodes:
       #    print j  
      # print self._nodes[1] 
      # print "\n"      
      # print self._nodes[2]
      # for k in self._hostsnodes:
       #   print k
       #print "\n"
       #for j in self._switchesnodes:
        #    print j
       #print self._hostsnodes[1]
       #print self._switchesnodes[3]
      # print "\n"
       #for h in self._allclassnodes:
       #    print h.getid()
        #   print h.getalllink()
       #print "\n"
       #paths = getAllPath(self._switchesnodes[3],self._switchesnodes[4],self._allclassnodes,self.nodegraph)
       #for path in paths:
       #    path.getpathlen()
       #    path.printpath()
       self.creatinputefile()
       self.create_linkinfodictfile()
    def getlinkinfo(self,apiaddr):     ##访问ryu中获取link信息的接口，并将相关数据收集起来
        global linkinfodict
        conn1= httplib.HTTPConnection(apiaddr)
        conn1.request("GET",self._links) 
        response1 = conn1.getresponse()
        str1 = response1.read()
        #print str1
        self._linksinfodict = json.loads(str1);
               
        for singlelink in self._linksinfodict:
            #print type(singlelink)
            #print type(singlelink["src"])
            #print singlelink["src"]
            
            linksrc=singlelink["src"]["dpid"]  ##获取link的src对应的端口dpid
            linkdst=singlelink["dst"]["dpid"]  ##获取link的dst对应的端口dpid
            
            self._nodeslink.setdefault(linksrc,[]).append(linkdst)  ##将形如[src,dst]:[src-port-dpid,dst-port-dpid]信息添加到邻接列表中
            #print self._nodeslink[linksrc] 
            self._linkinfodict[linksrc,linkdst] = [singlelink["src"]["port_no"],singlelink["dst"]["port_no"]] ##收集[src,dst] link对应的port号收集，以后下发流表时可能有用
           # print self._linkinfodict[linksrc,linkdst]
            #print self._nodeslink[linksrc]
       # print type(self._linksinfodict)
       # print type(self._nodeslink[linksrc])
        
       # print ob[1]
       # print ob[2]
       # print ob[3]
        
    def gethostsinfo(self,apiaddr):     ##访问ryu中获取hosts信息的接口，并将相关数据收集起来
        conn2= httplib.HTTPConnection(apiaddr)
        conn2.request("GET",self._hosts) 
        response2 = conn2.getresponse()
        str2 = response2.read()
        #print str2
        self._hostsinfodict = json.loads(str2);
        for singlehost in self._hostsinfodict:
            switch_to_hostinfo = singlehost["port"]
            switchdpid = switch_to_hostinfo["dpid"]
            switchport = switch_to_hostinfo["port_no"]
            hostmac = singlehost["mac"] 
            list_hostipv4 = singlehost["ipv4"] 
            hostipv4 = ""
	    for val in list_hostipv4:
                   hostipv4 = hostipv4+val
	    #print hostipv4
            self._hostsnodes.append(hostipv4)
            self._nodeslink.setdefault(hostipv4,[]).append(switchdpid)  ##主机host的邻接信息
            self._nodeslink.setdefault(switchdpid,[]).append(hostipv4)   ##将主机host添加到switches的邻接信息中
            self._host_to_switchinfo[hostipv4,switchdpid] = [hostmac,switchport]
            self._linkinfodict[hostipv4,switchdpid] = [hostmac,switchport]##后来修改加上的，可能有问题
            self._linkinfodict[switchdpid,hostipv4] = [switchport,hostmac] ##边是有向边
            #print self._host_to_switchinfo[hostmac,switchdpid]
            #print self._nodeslink[hostmac]
           # print self._nodeslink[switchdpid]  
        
    def getswitchesinfo(self,apiaddr):    ##访问ryu中获取switches信息的接口，并将相关数据收集起来
        conn3= httplib.HTTPConnection(apiaddr)
        conn3.request("GET",self._switches) 
        response3 = conn3.getresponse()
        str3 = response3.read()
        #print str3
        self._switchesinfo = json.loads(str3);
        ports = []
        for singleswitch in self._switchesinfo:
            self._switchesnodes.append(singleswitch["dpid"])
            portinfo = singleswitch["ports"] 
            ports = []        
            for singleport in portinfo:
                 ports.append(singleport["port_no"])                    
            self._switchportsinfo[singleswitch["dpid"]] = ports     ##各个switch所拥有的端口集合      
           # print self._switchportsinfo[singleswitch["dpid"]]
    def create_linkinfodictfile(self):
        f1 = open("_linkinfodict.txt",'w')
        f1.write(str(self._linkinfodict))
        f1.close()
    def creatinputefile(self):      ##创建__MC_ICC16_Alg1.py的输入文件
        f1=open("_PathSet.txt","w")
        f2=open("_Cap_MBoxes.txt","w")
        #f3=open("_Cap_links.txt","w")
        f4=open("_TrafficDemands.txt","w")
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
        f2.close()
        
        ID_TDnum = 0                    ##创建_TrafficDemands.txt文件
        for j in self._TDhosts:            
            str2 = "-nID_TD"+"\t"+str(ID_TDnum)+"\t"+"-Src"+"\t"+j+"\t"+"-nRate"+"\t"+"100"+"\n"
            f4.write(str2)
            ID_TDnum = ID_TDnum + 1
        f4.close()  
        """     
        for key in self._linkinfodict.keys():           ##创建_Cap_links.txt文件
            str3 = "Node_u"+"\t"+key[0]+"\t"+"-Node_v"+"\t"+key[1]+"\t"+"-Cap"+"\t"+"1000"+"\n"
            f3.write(str3)
        f3.close()    
        """   
        for i in self._Mboxnodes:    ##创建_PathSet.txt文件
            for j in self._TDhosts:                   
            #for j in self._switchesnodes:
                paths = getAllPath(j,i,self._allclassnodes,self.nodegraph)
                for path in paths:        
                    str4 = "-Dst"+"\t"+i+"\t"+"-Src"+"\t"+j+"\t"+"-pathLen"+"\t"+str(path.getpathlen())+"\t"+"-ReversePath"+"\t"+path.printpath()+"\n"
                    f1.write(str4)
        f1.close()
        
       
 
