#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import OVSKernelAP
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

from subprocess import call, check_call, check_output
import time

def MobileNet(topology, mptcpEnabled, congestCtl):

    call(["sudo", "sysctl", "-w", "net.mptcp.mptcp_enabled="+str(mptcpEnabled)])
    call(["sudo", "modprobe", "mptcp_coupled"])
    call(["sudo", "sysctl", "-w", "net.ipv4.tcp_congestion_control="+congestCtl])

    '''Parameters for simulation'''
    numOfAp = 3
    numOfLte = 1
    numOfSta = 3
    propModel = "logDistance"
    exponent = 4
    backhaulBW = 10
    backhaulDelay = 10
    backhaulLoss = 1
    lteBW = 1
    lteDelay = 10
    lteLoss = 1
    ethPerSta = 1
    wlanPerSta = 1

    '''Data needed for FDM'''
    users = []
    nets = []
    demand = {}
    capacity = {}
    delay = {}

    net = Mininet(controller=None, accessPoint=OVSKernelAP, link=TCLink, autoSetMacs=True)

    print "*** Creating nodes ***"
    nodes = {}

    '''Host : One host serves as a server'''
    node = net.addHost('h1', ip='10.0.0.1')
    nodes['h1'] = node

    '''Station : Defaultly set up the stations with 1 eth and 1 wlan interfaces'''
    for i in range(1, numOfSta+1):
        sta_name = 'sta'+str(i)
        node = net.addStation(sta_name)
        users.append(sta_name)
        nodes[sta_name] = node
        demand[sta_name] = 6

    '''Switch'''
    numOfSwitch = numOfAp+numOfLte*2+1                        # last one is for server h1
    for i in range(1, numOfSwitch+1):
        switch_name = 's'+str(i)
        node = net.addSwitch(switch_name)
        nodes[switch_name] = node

    '''Access Point'''
    for i in range(1, numOfAp+1):
        ap_name = 'ap'+str(i)
        ap_ssid = ap_name+'_ssid'
        ap_mode = 'g'
        ap_chan = '1'
        ap_pos = str(40+60*(i-1))+',100,0'
        ap_range = '40'
        node = net.addAccessPoint(ap_name, ssid=ap_ssid, mode=ap_mode, channel=ap_chan, position=ap_pos, range=ap_range)
        nets.append(ap_name)
        nodes[ap_name] = node

    print "*** Configuring propagation model ***"
    net.propagationModel(model=propModel, exp=exponent)

    print "*** Configuring wifi nodes ***"
    net.configureWifiNodes()

    print "*** Associating and Creating links ***"
    '''Backhaul links between switches'''
    for i in range(1, numOfAp+numOfLte+1):
        node_u = nodes['s'+str(numOfSwitch)]
        node_d = nodes['s'+str(i)]
        net.addLink(node_d, node_u, bw=float(backhaulBW), delay=str(backhaulDelay)+'ms', loss=float(backhaulLoss))
        capacity['s'+str(i)+'-s'+str(numOfSwitch)] = float(backhaulBW)
        delay['s'+str(i)+'-s'+str(numOfSwitch)] = float(backhaulDelay)

    '''Link between server and switch'''
    node_h = nodes['h1']
    node_d = nodes['s'+str(numOfSwitch)]
    net.addLink(node_d, node_h)

    '''Links between stations and LTE switch'''
    for i in range(1, numOfSta+1):
        node_lte = nodes['s'+str(numOfAp+numOfLte+1)]
        node_sta = nodes['sta'+str(i)]
        net.addLink(node_sta, node_lte, bw=float(lteBW), delay=str(lteDelay)+'ms', loss=float(lteLoss))
        capacity['sta'+str(i)+'-s'+str(numOfAp+1)] = float(lteBW)
        delay['sta'+str(i)+'-s'+str(numOfAp+1)] = float(lteDelay)

    '''Links between APs and switches'''
    for i in range(1, numOfAp+1):
        node_u = nodes['s'+str(i)]
        node_d = nodes['ap'+str(i)]
        net.addLink(node_d, node_u)

    '''Links between LTEs and switches'''
    for i in range(1, numOfLte+1):
        node_u = nodes['s'+str(numOfAp+i)]
        node_d = nodes['s'+str(numOfAp+numOfLte+i)]
        net.addLink(node_d, node_u)

    print "*** Building the graph of the simulation ***"
    net.plotGraph(max_x=260, max_y=220)

    print "*** Configuring mobility ***"
    net.startMobility(time=0, AC='ssf')
    net.mobility(nodes['sta1'], 'start', time=30, position='100,50,0')
    net.mobility(nodes['sta2'], 'start', time=30, position='50,50,0')
    net.mobility(nodes['sta3'], 'start', time=30, position='150,50,0')
    net.mobility(nodes['sta1'], 'stop', time=40, position='145,100,0')
    net.mobility(nodes['sta2'], 'stop', time=40, position='145,100,0')
    net.mobility(nodes['sta3'], 'stop', time=40, position='145,100,0')
    net.stopMobility(time=70)

    print "*** Starting network simulation ***"
    net.start()

    print "*** Addressing for station ***"
    for i in range(1, numOfSta+1):
        sta_name = 'sta'+str(i)
        station = nodes[sta_name]
        for j in range(0, wlanPerSta):
            station.cmd('ifconfig '+sta_name+'-wlan'+str(j)+' 10.0.'+str(i+1)+'.'+str(j)+'/32')
            station.cmd('ip rule add from 10.0.'+str(i+1)+'.'+str(j)+' table '+str(j+1))
            station.cmd('ip route add 10.0.'+str(i+1)+'.'+str(j)+'/32 dev '+sta_name+'-wlan'+str(j)+' scope link table '+str(j+1))
            station.cmd('ip route add default via 10.0.'+str(i+1)+'.'+str(j)+' dev '+sta_name+'-wlan'+str(j)+' table '+str(j+1))
            if j == 0:
                station.cmd('ip route add default scope global nexthop via 10.0.'+str(i+1)+'.'+str(j)+' dev '+sta_name+'-wlan'+str(j))
        for j in range(wlanPerSta, ethPerSta+wlanPerSta):
            station.cmd('ifconfig '+sta_name+'-eth'+str(j)+' 10.0.'+str(i+1)+'.'+str(j)+'/32')
            station.cmd('ip rule add from 10.0.'+str(i+1)+'.'+str(j)+' table '+str(j+1))
            station.cmd('ip route add 10.0.'+str(i+1)+'.'+str(j)+'/32 dev '+sta_name+'-eth'+str(j)+' scope link table '+str(j+1))
            station.cmd('ip route add default via 10.0.'+str(i+1)+'.'+str(j)+' dev '+sta_name+'-eth'+str(j)+' table '+str(j+1))

    time.sleep(70)

    print "*** Stopping network ***"
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    repeatTimes = 1
    mptcpEnabled = 1
    congestCtl = 'cubic'
    for i in range(0, repeatTimes):
        MobileNet("topology/test.txt", mptcpEnabled, congestCtl)