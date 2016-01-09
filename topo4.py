from mininet.topo import Topo
 
 
class MyTopo(Topo):
    "Simple loop topology example."
 
    def __init__(self):
        "Create custom loop topo."
 
        # Initialize topology
        Topo.__init__(self)
 
        # Add hosts 
        host1 = self.addHost('h1')
        host2 = self.addHost('h2')
        host3 = self.addHost('h3')
        host4 = self.addHost('h4')
        host5 = self.addHost('h5')
        host6 = self.addHost('h6')
        # Add switches
        switch1 = self.addSwitch("s1")
        switch2 = self.addSwitch("s2")
        switch3 = self.addSwitch("s3")
        switch4 = self.addSwitch("s4")
        switch5 = self.addSwitch("s5")
 
        # Add links
        self.addLink(switch1, host1, 1)
        self.addLink(switch1, host2, 2)
        self.addLink(switch1, switch2, 4, 3)
        self.addLink(switch1, switch4, 5, 3)
        self.addLink(switch1, switch5, 3, 3)
        self.addLink(switch2, host5, 1)
        #self.addLink(switch2, switch1, 3, 4)
        self.addLink(switch2, switch3, 2, 2)
        self.addLink(switch3, host4, 1)
        #self.addLink(switch3, switch2, 2, 2)
        self.addLink(switch3, switch4, 4, 2)
        self.addLink(switch3, switch5, 3, 2)
        self.addLink(switch4, host3, 1)
       # self.addLink(switch4, switch1, 3, 5)
        #self.addLink(switch4, switch3, 2, 4)
        self.addLink(switch5, host6, 1)
        #self.addLink(switch5, switch1, 3, 3)
       # self.addLink(switch5, switch3, 2, 3)
 
 
topos = {'mytopo': (lambda: MyTopo())}
