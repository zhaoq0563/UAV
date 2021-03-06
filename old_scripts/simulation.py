#!/usr/bin/python

from mininet.fdm_intf_handoff import FDM
from mininet.net import Mininet
from mininet.node import OVSKernelAP
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info

from subprocess import call
import time, random, os, sys


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


def deployStation(numOfAp, numOfSPSta, numOfMPSta, numOfFixApSta, assoOfFixApSta, numOfFixLteSta, assoOfFixLteSta, paramOfAp, paramOfSta, replay, config):
    start = 1
    for i in range(1, numOfSPSta+numOfMPSta+1):
        sta_name = 'sta'+str(i)
        if start>numOfAp:
            start = 1
        ap_name = 'ap'+str(start)
        paramOfSta[sta_name] = {}
        paramOfSta[sta_name]['ap'] = start
        if replay==1:
            sPos = config.readline().strip('\n')
        else:
            sPos = getPos(paramOfAp[ap_name][0], paramOfAp[ap_name][1])
            config.write(sPos+'\n')
        paramOfSta[sta_name]['sPos'] = sPos
        start += 1

    for (i, j) in zip(range(numOfSPSta+numOfMPSta+1, numOfSPSta+numOfMPSta+numOfFixApSta+1), range(0, numOfFixApSta)):
        sta_name = 'sta'+str(i)
        ap_name = 'ap'+str(assoOfFixApSta[j])
        paramOfSta[sta_name] = {}
        paramOfSta[sta_name]['ap'] = assoOfFixApSta[j]
        if replay==1:
            sPos = config.readline().strip('\n')
        else:
            sPos = getPos(paramOfAp[ap_name][0], paramOfAp[ap_name][1])
            config.write(sPos+'\n')
        paramOfSta[sta_name]['sPos'] = sPos

    for (i, j) in zip(range(numOfSPSta+numOfMPSta+numOfFixApSta+1, numOfSPSta+numOfMPSta+numOfFixApSta+numOfFixLteSta+1), range(0, numOfFixLteSta)):
        sta_name = 'sta'+str(i)
        ap_name = 's'+str(assoOfFixLteSta[j])
        paramOfSta[sta_name] = {}
        if replay==1:
            sPos = config.readline().strip('\n')
        else:
            sPos = str(random.randint(1, 10))+','+str(random.randint(1, 10))+',0'
            config.write(sPos+'\n')
        paramOfSta[sta_name]['sPos'] = sPos


def loadMobilityParams(paramOfSta, mobileSta, config):
    line = config.readline()
    while line!='':
        sta_name = line.strip('\n')
        mobileSta.append(sta_name)
        sTime = int(config.readline().strip('\n'))
        paramOfSta[sta_name]['sTime'] = sTime
        ePos = config.readline().strip('\n')
        paramOfSta[sta_name]['ePos'] = ePos
        eTime = int(config.readline().strip('\n'))
        paramOfSta[sta_name]['eTime'] = eTime
        line = config.readline()


def deployMobility(mode, *args):
    if mode=='equallyRandom':
        equRanMobility(*args)
    elif mode=='randomCongest':
        ranConMobility(*args)


def equRanMobility(*args):
    (numOfAp, paramOfAp, numOfSta, paramOfSta, mSta, mobileSta, config) = args
    mStaSet = random.sample(range(1, numOfSta+1), mSta)
    for i in range(1, mSta+1):
        sta_name = 'sta'+str(mStaSet[i-1])
        mobileSta.append(sta_name)                                                              # decide which sta to move
        speed = random.uniform(3, 5)                                                            # decide the speed for the sta
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
        config.write(sta_name+'\n')
        config.write(str(paramOfSta[sta_name]['sTime'])+'\n')
        config.write(paramOfSta[sta_name]['ePos']+'\n')
        config.write(str(paramOfSta[sta_name]['eTime'])+'\n')


def ranConMobility(*args):
    (numOfAp, paramOfAp, numOfSta, paramOfSta, mSta, mobileSta, config) = args
    mSta = numOfSta                                                                             # decide all sta move
    desAp = random.randint(1, numOfAp)                                                          # decide the destination ap
    ap_name = 'ap'+str(desAp)
    for i in range(1, mSta+1):
        speed = random.uniform(0.5, 1)                                                          # decide the speed for the sta
        sta_name = 'sta'+str(i)
        paramOfSta[sta_name]['desAp'] = desAp
        paramOfSta[sta_name]['sTime'] = random.randint(1, 20)                                   # decide the start time
        paramOfSta[sta_name]['ePos'] = getPos(paramOfAp[ap_name][0], paramOfAp[ap_name][1])     # decide the end position
        sX = int(paramOfSta[sta_name]['sPos'].split(',')[0])
        sY = int(paramOfSta[sta_name]['sPos'].split(',')[1])
        eX = int(paramOfSta[sta_name]['ePos'].split(',')[0])
        eY = int(paramOfSta[sta_name]['ePos'].split(',')[1])
        distance = ((eX-sX)**2+(eY-sY)**2)**0.5
        paramOfSta[sta_name]['eTime'] = paramOfSta[sta_name]['sTime']+int(distance/speed)       # decide the end time
        config.write(sta_name+'\n')
        config.write(str(paramOfSta[sta_name]['sTime'])+'\n')
        config.write(paramOfSta[sta_name]['ePos']+'\n')
        config.write(str(paramOfSta[sta_name]['eTime'])+'\n')


def setMobility(net, nodes, mobileSta, paramOfSta):
    max = 0
    for i in mobileSta:
        print i + ':' + str(paramOfSta[i]['sTime']) + '  ' + paramOfSta[i]['sPos'] + '   ' + str(paramOfSta[i]['eTime']) + '  ' + paramOfSta[i]['ePos']
        net.mobility(nodes[i], 'start', time=paramOfSta[i]['sTime'], position=paramOfSta[i]['sPos'])
        net.mobility(nodes[i], 'stop', time=paramOfSta[i]['eTime'], position=paramOfSta[i]['ePos'])
        if paramOfSta[i]['eTime']>max:
            max = paramOfSta[i]['eTime']
    return max


def sendingDITGTraffic(nodes, folderName, numOfSPSta, numOfMPSta, numOfFixApSta, numOfFixLteSta, demand, mEnd, MPStaSet, ethPerSta, wlanPerSta):
    print "*** Starting D-ITG Server on host ***"
    host = nodes['h1']
    info('Starting D-ITG server...\n')
    host.cmd('pushd ~/D-ITG-2.8.1-r1023/bin')
    host.cmd('./ITGRecv &')
    host.cmd('PID=$!')
    host.cmd('popd')
    if not os.path.exists(folderName):
        os.mkdir(folderName)
        user = os.getenv('SUDO_USER')
        os.system('sudo chown -R ' + user + ':' + user + ' ' + folderName)
    host.cmd('tcpdump -i h1-eth0 -w ' + folderName + '/h1.pcap &')

    print "*** Starting D-ITG Clients on stations ***"
    info('Starting D-ITG clients...\n')
    time.sleep(1)
    for i in range(1, numOfSPSta+numOfMPSta+numOfFixApSta+numOfFixLteSta+1):
        sender = nodes['sta'+str(i)]
        receiver = nodes['h'+str(1)]
        bwReq = demand['sta'+str(i)]*250
        ITGTest(sender, receiver, bwReq, (mEnd-1)*1000)
        if i<=numOfSPSta+numOfMPSta and i in MPStaSet:
            for j in range(0, wlanPerSta):
                sender.cmd('tcpdump -i sta'+str(i)+'-wlan'+str(j)+' -w '+folderName+'/sta'+str(i)+'-wlan'+str(j)+'.pcap &')
            for j in range(wlanPerSta, ethPerSta+wlanPerSta):
                sender.cmd('tcpdump -i sta'+str(i)+'-eth'+str(j)+' -w '+folderName+'/sta'+str(i)+'-eth'+str(j)+'.pcap &')
        elif i<=numOfSPSta+numOfMPSta+numOfFixApSta:
            sender.cmd('tcpdump -i sta'+str(i)+'-wlan0 -w '+folderName+'/sta'+str(i)+'-wlan0.pcap &')
        else:
            sender.cmd('tcpdump -i sta'+str(i)+'-eth1 -w '+folderName+'/sta'+str(i)+'-eth1.pcap &')


def sendingIperfTraffic(nodes, folderName, numOfSPSta, numOfMPSta, numOfFixApSta, numOfFixLteSta, mEnd, MPStaSet, ethPerSta, wlanPerSta):
    print "*** Starting iPerf Server on host ***"
    host = nodes['h1']
    info('Starting iPerf server...\n')
    host.cmd('iperf -s &')
    host.cmd('PID=$!')
    if not os.path.exists(folderName):
        os.mkdir(folderName)
        user = os.getenv('SUDO_USER')
        os.system('sudo chown -R '+user+':'+user+' '+folderName)
    host.cmd('tcpdump -i h1-eth0 -w '+folderName+'/h1.pcap &')

    print "*** Starting iPerf Clients on stations ***"
    info('Starting iPerf clients...\n')
    time.sleep(1)
    for i in range(1, numOfSPSta+numOfMPSta+numOfFixApSta+numOfFixLteSta+1):
        sender = nodes['sta'+str(i)]
        sender.cmd('iperf -c 10.0.0.1 -t '+str(mEnd)+' &')
        sender.cmd('PID_' + sender.name + '=$!')
        if i<=numOfSPSta+numOfMPSta and i in MPStaSet:
            for j in range(0, wlanPerSta):
                sender.cmd('tcpdump -i sta'+str(i)+'-wlan'+str(j)+' -w '+folderName+'/sta'+str(i)+'-wlan'+str(j)+'.pcap &')
            for j in range(wlanPerSta, ethPerSta+wlanPerSta):
                sender.cmd('tcpdump -i sta'+str(i)+'-eth'+str(j)+' -w '+folderName+'/sta'+str(i)+'-eth'+str(j)+'.pcap &')
        elif i<=numOfSPSta+numOfMPSta+numOfFixApSta:
            sender.cmd('tcpdump -i sta'+str(i)+'-wlan0 -w '+folderName+'/sta'+str(i)+'-wlan0.pcap &')
        else:
            sender.cmd('tcpdump -i sta'+str(i)+'-eth1 -w '+folderName+'/sta'+str(i)+'-eth1.pcap &')


def ITGTest(client, server, bw, sTime):
    info('Sending message from ', client.name, '<->', server.name, '\n')
    client.cmd('pushd ~/D-ITG-2.8.1-r1023/bin')
    client.cmdPrint('./ITGSend -T TCP -a 10.0.0.1 -c 500 -m rttm -O '+str(bw)+' -t '+str(sTime)+' -l log/'+str(client.name)+'.log -x log/'+str(client.name)+'-'+str(server.name)+'.log &')
    client.cmd('PID_'+client.name+'=$!')
    client.cmd('popd')

def Iperf3Test(client, server, bw, sTime):
    info('Sending message from ', client.name, '<->', server.name, '\n')
    client.cmdPrint("iperf3 -c 10.0.0.1 -b "+str(bw)+"M -t "+str(sTime) +" &")

def mobileNet(name, mptcpEnabled, fdmEnabled, congestCtl, trafficGen, replay, configFile):

    call(["sudo", "sysctl", "-w", "net.mptcp.mptcp_enabled="+str(mptcpEnabled)])
    call(["sudo", "modprobe", "mptcp_coupled"])
    call(["sudo", "modprobe", "tcp_hybla"]) if (congestCtl=='hybla') else congestCtl
    call(["sudo", "modprobe", "mptcp_rr"])
    call(["sudo", "sysctl", "-w", "net.mptcp.mptcp_scheduler=roundrobin"])
    call(["sudo", "sysctl", "-w", "net.ipv4.tcp_congestion_control="+congestCtl])

    '''Parameters for simulation
       Parameter:  propModel:  (logDistance)
                   acMode:     (ssf, llf)
                   mobiMode:   (equallyRandom, randomCongest)
    '''

    print "*** Loading the parameters for simulation ***"
    params = []
    config = open(configFile, 'r+')
    line = config.readline()
    while line!='END' and line!='END\n':
        print line
        params.append(eval(line.strip('\n').split(':')[1]))
        line = config.readline()
    if not replay:
        config.truncate()
        if line=='END':
            config.write('\n')
    (numOfAp, numOfLte, numOfSPSta, numOfMPSta, numOfFixApSta, assoOfFixApSta, numOfFixLteSta, assoOfFixLteSta, backhaulBW, backhaulDelay, backhaulLoss, lteBW, lteDelay, lteLoss) = params

    propModel = "logDistance"
    exponent = 4
    ethPerSta = 1
    wlanPerSta = 1
    mStart = 0
    mEnd = 100
    acMode = 'ssf'
    mobiMode = 'equallyRandom'
    folderName = 'pcap_'+name

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
        if i>numOfAp+numOfLte and i!=numOfSwitch:
            nets.append(switch_name)

    '''Access Point'''
    for i in range(1, numOfAp+1):
        ap_name = 'ap'+str(i)
        ap_ssid = ap_name+'_ssid'
        ap_mode = 'g'
        ap_chan = '1'
        ap_range = '40'

        if replay==1:
            ap_pos = config.readline().strip('\n')
        else:
            ap_pos = str(40+60*(i-1))+',100,0'
            config.write(ap_pos+'\n')

        paramOfAp[ap_name] = [ap_pos, ap_range]
        node = net.addAccessPoint(ap_name, ssid=ap_ssid, mode=ap_mode, channel=ap_chan, position=ap_pos, range=ap_range)
        nets.append(ap_name)
        nodes[ap_name] = node

    '''Update the position of each station'''
    deployStation(numOfAp, numOfSPSta, numOfMPSta, numOfFixApSta, assoOfFixApSta, numOfFixLteSta, assoOfFixLteSta, paramOfAp, paramOfSta, replay, config)

    '''Station : Defaultly set up the stations with 1 eth and 1 wlan interfaces'''
    for i in range(1, numOfSPSta+numOfMPSta+numOfFixApSta+numOfFixLteSta+1):
        sta_name = 'sta'+str(i)
        if i<=numOfSPSta+numOfMPSta:
            node = net.addStation(sta_name)
        else:
            node = net.addStation(sta_name, position=paramOfSta[sta_name]['sPos'])
        users.append(sta_name)
        nodes[sta_name] = node
        demand[sta_name] = 3

    print "*** Configuring propagation model ***"
    net.propagationModel(model=propModel, exp=exponent)

    print "*** Configuring wifi nodes ***"
    net.configureWifiNodes()

    print "*** Associating and Creating links ***"
    '''Backhaul links between switches'''
    for i in range(1, numOfAp+numOfLte+1):
        node_u = nodes['s'+str(numOfSwitch)]
        node_d = nodes['s'+str(i)]
        net.addLink(node_d, node_u, bw=float(backhaulBW[i-1]), delay=str(backhaulDelay[i-1])+'ms', loss=float(backhaulLoss[i-1]))
        capacity['s'+str(i)+'-s'+str(numOfSwitch)] = float(backhaulBW[i-1])
        delay['s'+str(i)+'-s'+str(numOfSwitch)] = float(backhaulDelay[i-1])

    '''Link between server and switch'''
    node_h = nodes['h1']
    node_d = nodes['s'+str(numOfSwitch)]
    net.addLink(node_d, node_h)

    '''Links between stations and LTE switch'''
    # MPStaSet = random.sample(range(1, numOfSPSta+numOfMPSta+1), numOfMPSta)
    MPStaSet = [1, 2]
    for i in MPStaSet:
        node_lte = nodes['s'+str(numOfAp+numOfLte+1)]
        node_sta = nodes['sta'+str(i)]
        net.addLink(node_sta, node_lte, bw=float(lteBW), delay=str(lteDelay)+'ms', loss=float(lteLoss))
        capacity[node_sta.name+'-'+node_lte.name] = float(lteBW)
        delay[node_sta.name+'-'+node_lte.name] = float(lteDelay)
    for (i, j) in zip(range(numOfSPSta+numOfMPSta+numOfFixApSta+1, numOfSPSta+numOfMPSta+numOfFixApSta+numOfFixLteSta+1), range(0, numOfFixLteSta)):
        node_lte = nodes['s'+str(assoOfFixLteSta[j])]
        node_sta = nodes['sta'+str(i)]
        net.addLink(node_sta, node_lte, bw=float(lteBW), delay=str(lteDelay)+'ms', loss=float(lteLoss))
        capacity[node_sta.name+'-'+node_lte.name] = float(lteBW)
        delay[node_sta.name+'-'+node_lte.name] = float(lteDelay)

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

    print users
    print nets
    print demand
    print capacity
    print delay

    print "*** Building the graph of the simulation ***"
    net.plotGraph(max_x=260, max_y=220)

    print "*** Configuring mobility ***"
    # net.startMobility(time=mStart, AC=acMode)
    # net.mobility(nodes['sta1'], 'start', time=5, position='120,99,0')
    # net.mobility(nodes['sta1'], 'stop', time=95, position='55,99,0')
    # net.mobility(nodes['sta2'], 'start', time=5, position='120,101,0')
    # net.mobility(nodes['sta2'], 'stop', time=95, position='55,101,0')

    # if replay==1:
    #     loadMobilityParams(paramOfSta, mobileSta, rConfig)
    #     rConfig.close()
    # else:
    #     deployMobility(mobiMode, numOfAp, paramOfAp, numOfSta, paramOfSta, mSta, mobileSta, wConfig)
    #     wConfig.close()
    # mEnd = setMobility(net, nodes, mobileSta, paramOfSta)

    # net.stopMobility(time=mEnd)

    # net.seed(20)          # need to figure out what is seed

    #net.startMobility(time=mStart, AC=acMode, model='RandomDirection', max_x=185, max_y=125, min_x=15, min_y=75, max_v=0.8, min_v=0.4)
    net.startMobility(time=mStart, AC=acMode, model='RandomDirection', max_x=90, max_y=150, min_x=0, min_y=50,
                      max_v=0.8, min_v=0.4)
    net.stopMobility(time=mEnd)

    config.close()

    print "*** Starting network simulation ***"
    net.start()

    print "*** Addressing for station ***"
    for i in MPStaSet:
        sta_name = 'sta'+str(i)
        station = nodes[sta_name]
        for j in range(0, wlanPerSta):
            station.cmd('ifconfig '+sta_name+'-wlan'+str(j)+' 10.0.'+str(i+1)+'.'+str(j)+'/32')
            station.cmd('ip rule add from 10.0.'+str(i+1)+'.'+str(j)+' table '+str(j+1))
            station.cmd('ip route add 10.0.'+str(i+1)+'.'+str(j)+'/32 dev '+sta_name+'-wlan'+str(j)+' scope link table '+str(j+1))
            station.cmd('ip route add default via 10.0.'+str(i+1)+'.'+str(j)+' dev '+sta_name+'-wlan'+str(j)+' table '+str(j+1))
        for j in range(wlanPerSta, ethPerSta+wlanPerSta):
            station.cmd('ifconfig '+sta_name+'-eth'+str(j)+' 10.0.'+str(i+1)+'.'+str(j)+'/32')
            station.cmd('ip rule add from 10.0.'+str(i+1)+'.'+str(j)+' table '+str(j+1))
            station.cmd('ip route add 10.0.'+str(i+1)+'.'+str(j)+'/32 dev '+sta_name+'-eth'+str(j)+' scope link table '+str(j+1))
            station.cmd('ip route add default via 10.0.'+str(i+1)+'.'+str(j)+' dev '+sta_name+'-eth'+str(j)+' table '+str(j+1))
            if j==1:
                station.cmd('ip route add default scope global nexthop via 10.0.'+str(i+1)+'.'+str(j)+' dev '+sta_name+'-eth'+str(j))
    for i in range(1, numOfSPSta+numOfMPSta+1):
        if i not in MPStaSet:
            sta_name = 'sta'+str(i)
            station = nodes[sta_name]
            station.cmd('ifconfig '+sta_name+'-wlan0 10.0.'+str(i+1)+'.0/32')
            station.cmd('ip route add default via 10.0.'+str(i+1)+'.0 dev '+sta_name+'-wlan0')
    for i in range(numOfSPSta+numOfMPSta+1, numOfSPSta+numOfMPSta+numOfFixApSta+1):
        sta_name = 'sta'+str(i)
        station = nodes[sta_name]
        station.cmd('ifconfig '+sta_name+'-wlan0 10.0.'+str(i+1)+'.0/32')
        station.cmd('ip route add default via 10.0.'+str(i+1)+'.0 dev '+sta_name+'-wlan0')
    for i in range(numOfSPSta+numOfMPSta+numOfFixApSta+1, numOfSPSta+numOfMPSta+numOfFixApSta+numOfFixLteSta+1):
        sta_name = 'sta'+str(i)
        station = nodes[sta_name]
        station.cmd('ifconfig '+sta_name+'-eth1 10.0.'+str(i+1)+'.1/32')
        station.cmd('ifconfig '+sta_name +'-wlan0 10.0.'+str(i+1)+'.0/32')
        station.cmd('ip route add default scope global nexthop via 10.0.'+str(i+1)+'.1 dev '+station.name+'-eth1')

    print "*** Starting FDM ***"
    if mptcpEnabled and fdmEnabled:
        protocol = 'FDM'
    elif mptcpEnabled:
        protocol = 'MPTCP'
    else:
        protocol = 'SPTCP'

    FDM(net, users, nets, demand, capacity, delay, 0, mEnd, 2, bool(fdmEnabled), protocol)
    time.sleep(5)

    # print "***Running CLI"
    # CLI(net)

    print "*** Starting to generate the traffic ***"
    if trafficGen=='ditg':
        sendingDITGTraffic(nodes, folderName, numOfSPSta, numOfMPSta, numOfFixApSta, numOfFixLteSta, demand, mEnd-5, MPStaSet, ethPerSta, wlanPerSta)
    elif trafficGen=='iperf':
        sendingIperfTraffic(nodes, folderName, numOfSPSta, numOfMPSta, numOfFixApSta, numOfFixLteSta, mEnd-5, MPStaSet, ethPerSta, wlanPerSta)
    else:
        info('Wrong traffic generator selected.\n')

    print "*** Simulation is running. Please wait... ***"
    time.sleep(mEnd-5)

    # print "*** Stopping FDM ***"
    # fdm.terminateT()

    print "*** Stopping traffic generator on host ***"
    nodes['h1'].cmd('kill $PID')
    for i in range(1, numOfMPSta+numOfSPSta+numOfFixApSta+numOfFixLteSta+1):
        nodes['sta'+str(i)].cmd('kill $PID_'+nodes['sta'+str(i)].name)

    print "*** Data processing ***"
    for i in range(1, numOfSPSta+numOfMPSta+numOfFixApSta+numOfFixLteSta+1):
        if i<=numOfSPSta+numOfMPSta and i in MPStaSet:
            for j in range(0, wlanPerSta):
                ip = '10.0.'+str(i+1)+'.'+str(j)
                if mptcpEnabled:
                    out_f = folderName+'/sta'+str(i)+'-wlan'+str(j)+'_mptcp.stat'
                else:
                    out_f = folderName+'/sta'+str(i)+'-wlan'+str(j)+'_sptcp.stat'
                nodes['sta'+str(i)].cmdPrint('sudo tshark -r '+folderName+'/sta'+str(i)+'-wlan'+str(j)+'.pcap -qz \"io,stat,0,BYTES()ip.src=='+ip+',AVG(tcp.analysis.ack_rtt)tcp.analysis.ack_rtt&&ip.addr=='+ip+'\" >'+out_f)
            for j in range(wlanPerSta, ethPerSta+wlanPerSta):
                ip = '10.0.'+str(i+1)+'.'+str(j)
                if mptcpEnabled:
                    out_f = folderName + '/sta' + str(i) + '-eth' + str(j) + '_mptcp.stat'
                else:
                    out_f = folderName + '/sta' + str(i) + '-eth' + str(j) + '_sptcp.stat'
                nodes['sta'+str(i)].cmdPrint('sudo tshark -r '+folderName+'/sta'+str(i)+'-eth'+str(j)+'.pcap -qz \"io,stat,0,BYTES()ip.src=='+ip+',AVG(tcp.analysis.ack_rtt)tcp.analysis.ack_rtt&&ip.addr=='+ip+'\" >'+out_f)
        elif i<=numOfSPSta+numOfMPSta+numOfFixApSta:
            ip ='10.0.'+str(i+1)+'.0'
            if mptcpEnabled:
                out_f = folderName+'/sta'+str(i)+'-wlan0_mptcp.stat'
            else:
                out_f = folderName+'/sta'+str(i)+'-wlan0_sptcp.stat'
            nodes['sta'+str(i)].cmdPrint('sudo tshark -r '+folderName+'/sta'+str(i)+'-wlan0.pcap -qz \"io,stat,0,BYTES()ip.src=='+ip+',AVG(tcp.analysis.ack_rtt)tcp.analysis.ack_rtt&&ip.addr=='+ip+'\" >'+out_f)
        else:
            ip = '10.0.'+str(i+1)+'.0'
            if mptcpEnabled:
                out_f = folderName+'/sta'+str(i)+'-eth1_mptcp.stat'
            else:
                out_f = folderName+'/sta'+str(i)+'-eth1_sptcp.stat'
            nodes['sta'+str(i)].cmdPrint('sudo tshark -r '+folderName+'/sta'+str(i)+'-eth1.pcap -qz \"io,stat,0,BYTES()ip.src=='+ip+',AVG(tcp.analysis.ack_rtt)tcp.analysis.ack_rtt&&ip.addr=='+ip+'\" >'+out_f)
    if trafficGen == 'ditg':
        os.system('sudo python analysis.py '+(str(range(1, numOfSPSta+numOfMPSta+numOfFixApSta+numOfFixLteSta+1))).replace(' ', '')+' '+folderName)

    print "*** Stopping network ***"
    net.stop()


if __name__ == '__main__':
    name = sys.argv[1]
    mptcpEnabled = int(sys.argv[2])
    fdmEnabled = int(sys.argv[3])
    congestCtl = sys.argv[4]
    trafficGen = sys.argv[5]
    replay = int(sys.argv[6])
    configName = sys.argv[7]
    mobileNet(name, mptcpEnabled, fdmEnabled, congestCtl, trafficGen, replay, configName)