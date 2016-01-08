#coding=utf-8

from ryu.base import app_manager

from ryu.controller import ofp_event

from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER

from ryu.controller.handler import set_ev_cls

from ryu.ofproto import ofproto_v1_0

from ryu.lib.packet import packet

from ryu.lib.packet import ethernet

from ryu.lib.packet import arp

from ryu.lib.mac import haddr_to_bin

 

ETHERNET = ethernet.ethernet.__name__

ETHERNET_MULTICAST = "ff:ff:ff:ff:ff:ff"

ARP = arp.arp.__name__

 

 

class simpleswitchofAlg1(app_manager.RyuApp):

    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

 

    def __init__(self, *args, **kwargs):

        super(simpleswitchofAlg1, self).__init__(*args, **kwargs)

        self.mac_to_port = {}

        self.arp_table = {}

        self.sw = {}



        self.Log_debug = open('Log_debug.txt','w');



        f4 = open("_linkinfodict.txt",'r')



        f5 = open("PathSet_selected.txt",'r')



        f6 = open("Paths_set.txt",'r')



        str_linkinfodict = f4.read()



        str_PathSet_selected = f5.read()



        str_Paths_set = f6.read() 



        f4.close()



        f5.close()



        f6.close()     



        self._linkinfodict =eval(str_linkinfodict)



        self.PathSet_selected = eval(str_PathSet_selected)



        self.Paths_set = eval(str_Paths_set)



        self.Log_debug.write("初始化完毕"+"\n" )



        self.Log_debug.write("self._linkinfodict"+" "+str(self._linkinfodict)+"\n")



        self.Log_debug.write("self.PathSet_selected"+"  "+str(self.PathSet_selected)+"\n")



        self.Log_debug.write("self.Paths_set"+"  "+str(self.Paths_set)+"\n")

 

    #def add_flow(self,datapath, priority,match,actions):

    def add_flow(self,datapath,priority,match,actions):

        ofproto = datapath.ofproto

        parser = datapath.ofproto_parser      

 

        #mod = parser.OFPFlowMod(datapath=datapath, match=match, cookie=0,command=ofproto.OFPFC_ADD, idle_timeout=30,          #hard_timeout=120,priority=ofproto.OFP_DEFAULT_PRIORITY,flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions)

        mod = parser.OFPFlowMod(datapath=datapath, match=match, cookie=0,command=ofproto.OFPFC_ADD, idle_timeout=3600,          hard_timeout=3600,priority=priority,flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions)

        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)

    def _packet_in_handler(self, ev):

        msg = ev.msg

        datapath = msg.datapath

        ofproto = datapath.ofproto

        parser = datapath.ofproto_parser

        in_port = msg.in_port

 

        pkt = packet.Packet(msg.data)

 

        eth = pkt.get_protocols(ethernet.ethernet)[0]

        dst = eth.dst

        src = eth.src

        dpid = datapath.id

        #self.Log_debug.write("dpid  "+str(dpid)+"\n")

        #self.Log_debug.write("typeofdpid "+str(type(dpid))+"\n")

        header_list = dict(

            (p.protocol_name, p)for p in pkt.protocols if type(p) != str)

        if ARP in header_list:

            self.arp_table[header_list[ARP].src_ip] = src  # ARP learning

 

        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

 

        # learn a mac address to avoid FLOOD next time.

        self.mac_to_port[dpid][src] = in_port

 

        if dst in self.mac_to_port[dpid]:

            #self.Log_debug.write("dst in self.mac_to_port"+"\n" )



            out_port = self.mac_to_port[dpid][dst]

            

        else:

            #self.Log_debug.write("dst not in self.mac_to_port"+"\n" )

            if self.arp_handler(header_list, datapath, in_port, msg.buffer_id):

                # 1:reply or drop;  0: flood

                self.Log_debug.write("ARP_PROXY_13"+"\n")

                return None

            else:

                out_port = ofproto.OFPP_FLOOD

               # self.Log_debug.write('OFPP_FLOOD'+"\n")

 

        

        

        # install a flow to avoid packet_in next time

        if out_port != ofproto.OFPP_FLOOD:

            self.Log_debug.write("outport is not floodport\n")

            self.Log_debug.write("mac src: "+str(src)+" mac dst: "+str(dst)+"\n")

            if (src,dst)in self.PathSet_selected.keys():

              path_list = []

              self.Log_debug.write("(src,dst)in self.PathSet_selected.keys()"+"\n")

              str_path_list = self.Paths_set[int(self.PathSet_selected[(src,dst)][0])] ##此处是单路径，多路径是该如何处理

              

              

              for val in str_path_list:

                  if str_path_list.index(val) == 0 or str_path_list.index(val) ==  len(str_path_list)-1:

                       print str(val)+"\n"

                       print "str_path_list.index(val)"+str(str_path_list.index(val))+"\n"

                       path_list.append(val)

                  else:

                       path_list.append(int(val))

              self.Log_debug.write("src  "+str(src)+"  dst"+str(dst)+"  pathlist  "+str(path_list)+"\n")

              self.Log_debug.write("dpid  "+str(dpid)+"\n")
              if dpid in path_list:##不在solution中的switch同样收到了macsrc、macdst
                  

                  dpidindex = path_list.index(dpid)

                  self.Log_debug.write("dpidindex  "+str(dpidindex)+"\n")



                  nextdpidindex = dpidindex+1

              

                  strdpid = str_path_list[dpidindex]

                  strnextdpid = str_path_list[nextdpidindex]

                  self.Log_debug.write("strdpid: "+strdpid+"strnextdpid: "+strnextdpid+"\n")

                  out_port = self._linkinfodict[strdpid,strnextdpid][0] ##求出packet应该转发的端口号

                  self.Log_debug.write("out_port: " +out_port+"\n")

              

                  actions = [parser.OFPActionOutput(int(out_port))]

                  match = datapath.ofproto_parser.OFPMatch( in_port=in_port, dl_src=haddr_to_bin(src), dl_dst=haddr_to_bin(dst))

                  self.add_flow(datapath, int(10),match, actions)

                  self.Log_debug.write("flow add\n")

                  data = None

                  if msg.buffer_id == ofproto.OFP_NO_BUFFER:

                     data = msg.data

                  out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,

                                  in_port=in_port, actions=actions, data=data)

                  datapath.send_msg(out)

                  self.Log_debug.write("packet out \n")
              else:
                  

                  out_port = self.mac_to_port[dpid][dst]

                  #self.Log_debug.write("out_port: " +str(out_port)+"\n")

                  actions = [parser.OFPActionOutput(out_port)]

                  match = datapath.ofproto_parser.OFPMatch( in_port=in_port, dl_dst=haddr_to_bin(dst))

                  self.add_flow(datapath, int(1),match, actions)

                 # self.Log_debug.write("flow add\n")     

                  data = None

                  if msg.buffer_id == ofproto.OFP_NO_BUFFER:

                    data = msg.data

                  out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,

                                  in_port=in_port, actions=actions, data=data)

                  datapath.send_msg(out) 

                  #self.Log_debug.write("packet out \n") 

            else:

              #self.Log_debug.write("(src,dst) is not in self.PathSet_selected.keys")

              out_port = self.mac_to_port[dpid][dst]

              #self.Log_debug.write("out_port: " +str(out_port)+"\n")

              actions = [parser.OFPActionOutput(out_port)]

              match = datapath.ofproto_parser.OFPMatch( in_port=in_port, dl_dst=haddr_to_bin(dst))

              self.add_flow(datapath, int(1),match, actions)

              #self.Log_debug.write("flow add\n")     

              data = None

              if msg.buffer_id == ofproto.OFP_NO_BUFFER:

                data = msg.data

              out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,

                                  in_port=in_port, actions=actions, data=data)

              datapath.send_msg(out) 

              #self.Log_debug.write("packet out \n")                  

        else:

           # self.Log_debug.write("outport is  floodport\n")

            actions = [parser.OFPActionOutput(out_port)]

            data = None

            if msg.buffer_id == ofproto.OFP_NO_BUFFER:

                data = msg.data

            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,

                                  in_port=in_port, actions=actions, data=data)

            datapath.send_msg(out)    

    def arp_handler(self, header_list, datapath, in_port, msg_buffer_id):

        header_list = header_list

        datapath = datapath

        in_port = in_port

 

        if ETHERNET in header_list:

            eth_dst = header_list[ETHERNET].dst

            eth_src = header_list[ETHERNET].src

 

        if eth_dst == ETHERNET_MULTICAST and ARP in header_list:

            arp_dst_ip = header_list[ARP].dst_ip

            if (datapath.id, eth_src, arp_dst_ip) in self.sw:  # Break the loop

                if self.sw[(datapath.id, eth_src, arp_dst_ip)] != in_port:

                    out = datapath.ofproto_parser.OFPPacketOut(

                        datapath=datapath,

                        buffer_id=datapath.ofproto.OFP_NO_BUFFER,

                        in_port=in_port,

                        actions=[], data=None)

                    datapath.send_msg(out)

                    return True

            else:

                self.sw[(datapath.id, eth_src, arp_dst_ip)] = in_port

 

        if ARP in header_list:

            hwtype = header_list[ARP].hwtype

            proto = header_list[ARP].proto

            hlen = header_list[ARP].hlen

            plen = header_list[ARP].plen

            opcode = header_list[ARP].opcode

 

            arp_src_ip = header_list[ARP].src_ip

            arp_dst_ip = header_list[ARP].dst_ip

 

            actions = []

 

            if opcode == arp.ARP_REQUEST:

                if arp_dst_ip in self.arp_table:  # arp reply

                    actions.append(datapath.ofproto_parser.OFPActionOutput(

                        in_port)

                    )

 

                    ARP_Reply = packet.Packet()

                    ARP_Reply.add_protocol(ethernet.ethernet(

                        ethertype=header_list[ETHERNET].ethertype,

                        dst=eth_src,

                        src=self.arp_table[arp_dst_ip]))

                    ARP_Reply.add_protocol(arp.arp(

                        opcode=arp.ARP_REPLY,

                        src_mac=self.arp_table[arp_dst_ip],

                        src_ip=arp_dst_ip,

                        dst_mac=eth_src,

                        dst_ip=arp_src_ip))

 

                    ARP_Reply.serialize()

 

                    out = datapath.ofproto_parser.OFPPacketOut(

                        datapath=datapath,

                        buffer_id=datapath.ofproto.OFP_NO_BUFFER,

                        in_port=datapath.ofproto.OFPP_CONTROLLER,

                        actions=actions, data=ARP_Reply.data)

                    datapath.send_msg(out)

                    return True

        return False

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)

    def _port_status_handler(self, ev):



        msg = ev.msg



        reason = msg.reason



        port_no = msg.desc.port_no







        ofproto = msg.datapath.ofproto



        if reason == ofproto.OFPPR_ADD:



            self.logger.info("port added %s", port_no)



        elif reason == ofproto.OFPPR_DELETE:



            self.logger.info("port deleted %s", port_no)



        elif reason == ofproto.OFPPR_MODIFY:



            self.logger.info("port modified %s", port_no)



        else:



            self.logger.info("Illeagal port state %s %s", port_no, reason)

      
