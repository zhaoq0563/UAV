#!/usr/bin/python

from mininet.fdm import FDM
from mininet.net import Mininet
from mininet.node import OVSKernelAP
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

from subprocess import call
import time, random


def getPos(center, range):
    c = center.split(',')
    r = int(range)
    while True:
        x = random.uniform(-r, r)
        y = random.uniform(-r, r)
        if (x**2)+(y**2)<(r**2) and (x**2)+(y**2)>(5**2):
            c[0] = str(int(c[0]) + int(x))
            c[1] = str(int(c[1]) + int(y))
            break
    return c[0]+','+c[1]+','+c[2]


def deployStation(numOfAp, numOfSta, paramOfAp, paramOfSta):
    start = 1
    for i in range(1, numOfSta+1):
        if start>numOfAp:
            start = 1
        ap_name = 'ap' + str(start)
        sta_name = 'sta' + str(i)
        paramOfSta[sta_name] = {}
        paramOfSta[sta_name]['sPos'] = getPos(paramOfAp[ap_name][0], paramOfAp[ap_name][1])
        paramOfSta[sta_name]['ap'] = start
        start += 1


def deployMobility(mode, *args):
    if mode=='equallyRandom':
        equRanMobility(*args)


def equRanMobility(*args):
    (numOfAp, paramOfAp, numOfSta, paramOfSta, mSta, mobileSta) = args
    result = random.sample(range(1, numOfSta+1), mSta)
    for i in range(1, mSta+1):
        sta_name = 'sta'+str(result[i-1])
        mobileSta.append(sta_name)                                                              # decide which sta to move
        speed = random.uniform(0.5, 1)                                                          # decide the speed for the sta
        while True:                                                                             # decide the destination ap
            desAp = random.randint(1, numOfAp)
            if desAp!=paramOfSta[sta_name]['ap']:
                paramOfSta[sta_name]['desAp']=desAp
                break
        paramOfSta[sta_name]['sTime'] = random.randint(1,20)                                    # decide the start time
        ap_name = 'ap'+str(paramOfSta[sta_name]['desAp'])
        paramOfSta[sta_name]['ePos'] = getPos(paramOfAp[ap_name][0], paramOfAp[ap_name][1])     # decide the end position
        sX = int(paramOfSta[sta_name]['sPos'].split(',')[0])
        sY = int(paramOfSta[sta_name]['sPos'].split(',')[1])
        eX = int(paramOfSta[sta_name]['ePos'].split(',')[0])
        eY = int(paramOfSta[sta_name]['ePos'].split(',')[1])
        distance = ((eX-sX)**2+(eY-sY)**2)**0.5
        paramOfSta[sta_name]['eTime'] = paramOfSta[sta_name]['sTime']+int(distance/speed)       # decide the end time


def setMobility(net, nodes, mobileSta, paramOfSta):
    max = 0
    for i in mobileSta:
        print i + ':' + str(paramOfSta[i]['sTime']) + '  ' + paramOfSta[i]['sPos'] + '   ' + str(paramOfSta[i]['eTime']) + '  ' + paramOfSta[i]['ePos'] + ' ' + str(paramOfSta[i]['ap']) + '->' + str(paramOfSta[i]['desAp'])
        net.mobility(nodes[i], 'start', time=paramOfSta[i]['sTime'], position=paramOfSta[i]['sPos'])
        net.mobility(nodes[i], 'stop', time=paramOfSta[i]['eTime'], position=paramOfSta[i]['ePos'])
        if paramOfSta[i]['eTime']>max:
            max = paramOfSta[i]['eTime']
    return max


def mobileNet(mptcpEnabled, congestCtl):

    call(["sudo", "sysctl", "-w", "net.mptcp.mptcp_enabled="+str(mptcpEnabled)])
    call(["sudo", "modprobe", "mptcp_coupled"])
    call(["sudo", "sysctl", "-w", "net.ipv4.tcp_congestion_control="+congestCtl])

    '''Parameters for simulation'''
    numOfAp = 3
    numOfLte = 1
    numOfSta = 5
    mSta = 3
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
    mStart = 0
    acMode = 'ssf'
    mobiMode = 'equallyRandom'

    '''Data needed for FDM'''
    users = []
    nets = []
    demand = {}
    capacity = {}
    delay = {}

    '''Date needed for mobility
    Parameter:  paramOfAp { key: str(AP name), value: [str(AP center position), str(AP range)] }
                mobileSta [ str(name of the moving station) ]
                paramOfSta { key: str(Station name), value: { key: 'ap',    value: (int)index of currently connected ap }
                                                            { key: 'desAp', value: (int)index of which ap the station goes }
                                                            { key: 'sPos',  value: (str)starting position of the station }
                                                            { key: 'ePos',  value: (str)ending position of the station }
                                                            { key: 'sTime', value: (int)starting time of the station }
                                                            { key: 'eTime', value: (int)ending time of the station }
                           }
    '''
    paramOfAp = {}
    mobileSta = []
    paramOfSta = {}

    net = Mininet(controller=None, accessPoint=OVSKernelAP, link=TCLink, autoSetMacs=True)

    print "*** Creating nodes ***"
    nodes = {}

    '''Host : One host serves as a server'''
    node = net.addHost('h1', ip='10.0.0.1')
    nodes['h1'] = node

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
        paramOfAp[ap_name] = [ap_pos, ap_range]
        node = net.addAccessPoint(ap_name, ssid=ap_ssid, mode=ap_mode, channel=ap_chan, position=ap_pos, range=ap_range)
        nets.append(ap_name)
        nodes[ap_name] = node

    '''Update the position of each station'''
    deployStation(numOfAp, numOfSta, paramOfAp, paramOfSta)

    '''Station : Defaultly set up the stations with 1 eth and 1 wlan interfaces'''
    for i in range(1, numOfSta + 1):
        sta_name = 'sta' + str(i)
        node = net.addStation(sta_name, position=paramOfSta[sta_name]['sPos'])
        users.append(sta_name)
        nodes[sta_name] = node
        demand[sta_name] = 6

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
    net.startMobility(time=mStart, AC=acMode)

    deployMobility(mobiMode, numOfAp, paramOfAp, numOfSta, paramOfSta, mSta, mobileSta)
    mEnd = setMobility(net, nodes, mobileSta, paramOfSta)+20

    net.stopMobility(time=mEnd)

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

    # print "***Running CLI"
    # CLI(net)

    print "*** Starting FDM ***"
    FDM(net, users, nets, demand, capacity, delay, 0, mEnd, 2)

    time.sleep(mEnd)

    print "*** Stopping network ***"
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    repeatTimes = 1
    mptcpEnabled = 1
    congestCtl = 'cubic'
    for i in range(0, repeatTimes):
        mobileNet(mptcpEnabled, congestCtl)