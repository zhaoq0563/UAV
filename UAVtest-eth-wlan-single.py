#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import OVSKernelAP
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from subprocess import call
import time, os


def ITGTest(client, server, bw, sTime):
    info('Sending message from ', client.name, '<->', server.name, '\n')
    client.cmd('pushd ~/D-ITG-2.8.1-r1023/bin')
    client.cmd('./ITGSend -T TCP -a 10.0.0.1 -c 1000 -O '+str(bw)+' -t '+str(sTime)+' -l log/'+str(client.name)+'.log -x log/'+str(client.name)+'-'+str(server.name)+'.log &')
    client.cmd('popd')


def topology(name):

    call(["sudo", "sysctl", "-w", "net.mptcp.mptcp_enabled=0"])
    call(["sudo", "modprobe", "mptcp_coupled"])
    call(["sudo", "sysctl", "-w", "net.ipv4.tcp_congestion_control=lia"])

    net = Mininet(controller=None, accessPoint=OVSKernelAP, link=TCLink, autoSetMacs=True)

    print "***Creating nodes..."
    nodes = {}
    h1 = net.addHost('h1', ip='10.0.0.1')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')
    s4 = net.addSwitch('s4')
    sta1 = net.addStation('sta1')        # for congestion
    sta2 = net.addStation('sta2')       # for congestion
    sta3 = net.addStation('sta3')         # for congestion
    ap1 = net.addAccessPoint('ap1', ssid='ap1-ssid', mode='g', channel='1', position='150,100,0', range='50')
    nodes['h1'] = h1
    nodes['s1'] = s1
    nodes['s2'] = s2
    nodes['s3'] = s3
    nodes['s4'] = s4
    nodes['sta1'] = sta1
    nodes['sta2'] = sta2
    nodes['sta3'] = sta3
    nodes['ap1'] = ap1

    print "***Configuring propagation model..."
    net.propagationModel(model="logDistance", exp=4)

    print "***Configuring wifi nodes..."
    net.configureWifiNodes()

    print "***Associating and Creating links..."
    net.addLink(sta1, s4)
    net.addLink(sta2, s4)
    net.addLink(sta3, s4)
    net.addLink(s4, s2)
    net.addLink(ap1, s3)
    net.addLink(s2, s1, bw=50, delay='250ms', loss=1)
    net.addLink(s3, s1, bw=1, delay='10ms', loss=1)
    net.addLink(s1, h1)

    net.plotGraph(max_x=220, max_y=180)

    net.startMobility(time=0, AC='ssf')
    net.mobility(sta1, 'start', time=10, position='50,80,0')
    net.mobility(sta2, 'start', time=10, position='50,50,0')
    net.mobility(sta3, 'start', time=10, position='80,50,0')
    net.mobility(sta1, 'stop', time=110, position='150,130,0')
    net.mobility(sta2, 'stop', time=110, position='155,105,0')
    net.mobility(sta3, 'stop', time=110, position='180,100,0')
    net.stopMobility(time=150)

    print "***Starting network"
    net.start()

    print "***Addressing for station..."
    sta1.cmd('ifconfig sta1-wlan0 10.0.1.0/32')
    sta1.cmd('ifconfig sta1-eth1 10.0.1.1/32')
    sta1.cmd('ip rule add from 10.0.1.0 table 1')
    sta1.cmd('ip rule add from 10.0.1.1 table 2')
    sta1.cmd('ip route add 10.0.1.0/32 dev sta1-wlan0 scope link table 1')
    sta1.cmd('ip route add default via 10.0.1.0 dev sta1-wlan0 table 1')
    sta1.cmd('ip route add 10.0.1.1/32 dev sta1-eth1 scope link table 2')
    sta1.cmd('ip route add default via 10.0.1.1 dev sta1-eth1 table 2')
    sta1.cmd('ip route add default scope global nexthop via 10.0.1.1 dev sta1-eth1')

    sta2.cmd('ifconfig sta2-wlan0 10.0.2.0/32')
    sta2.cmd('ifconfig sta2-eth1 10.0.2.1/32')
    sta2.cmd('ip rule add from 10.0.2.0 table 1')
    sta2.cmd('ip rule add from 10.0.2.1 table 2')
    sta2.cmd('ip route add 10.0.2.0/32 dev sta2-wlan0 scope link table 1')
    sta2.cmd('ip route add 10.0.2.1/32 dev sta2-eth1 scope link table 2')
    sta2.cmd('ip route add default via 10.0.2.0 dev sta2-wlan0 table 1')
    sta2.cmd('ip route add default via 10.0.2.1 dev sta2-eth1 table 2')
    sta2.cmd('ip route add default scope global nexthop via 10.0.2.1 dev sta2-eth1')

    sta3.cmd('ifconfig sta3-wlan0 10.0.3.0/32')
    sta3.cmd('ifconfig sta3-eth1 10.0.3.1/32')
    sta3.cmd('ip rule add from 10.0.3.0 table 1')
    sta3.cmd('ip rule add from 10.0.3.1 table 2')
    sta3.cmd('ip route add 10.0.3.0/32 dev sta3-wlan0 scope link table 1')
    sta3.cmd('ip route add default via 10.0.3.0 dev sta3-wlan0 table 1')
    sta3.cmd('ip route add 10.0.3.1/32 dev sta3-eth1 scope link table 2')
    sta3.cmd('ip route add default via 10.0.3.1 dev sta3-eth1 table 2')
    sta3.cmd('ip route add default scope global nexthop via 10.0.3.1 dev sta3-eth1')

    print "***Setting flow tables..."
    call(["sudo", "bash", "flowTable/ew-ftConfig.sh"])

    print "*** Starting D-ITG Server on host ***"
    host = nodes['h1']
    info('Starting D-ITG server...\n')
    host.cmd('pushd ~/D-ITG-2.8.1-r1023/bin')
    host.cmd('./ITGRecv &')
    host.cmdPrint('PID=$!')
    host.cmd('popd')
    folderName = 'pcap_'+name
    if not os.path.exists(folderName):
        os.mkdir(folderName)
        user = os.getenv('SUDO_USER')
        os.system('sudo chown -R '+user+':'+user+' '+folderName)
    host.cmd('tcpdump -i h1-eth0 -w '+folderName+'/h1.pcap &')

    print "*** Starting D-ITG Clients on stations ***"
    time.sleep(1)
    for i in range(1, 4):
        sender = nodes['sta'+str(i)]
        receiver = nodes['h'+str(1)]
        bwReq = 125
        ITGTest(sender, receiver, bwReq, 149*1000)
        for j in range(0, 1):
            sender.cmd('tcpdump -i sta'+str(i)+'-wlan'+str(j)+' -w '+folderName+'/sta'+str(i)+'-wlan'+str(j)+'.pcap &')
        for j in range(1, 2):
            sender.cmd('tcpdump -i sta'+str(i)+'-eth'+str(j)+' -w '+folderName+'/sta'+str(i)+'-eth'+str(j)+'.pcap &')
    print "*** Simulation is running. Please wait... ***"

    time.sleep(60)
    print "*** Deleting the link between stations and STACOM ***"
    net.delLinkBetween(sta1, s4)
    net.delLinkBetween(sta2, s4)
    net.delLinkBetween(sta3, s4)
    sta1.cmd("ip route del default scope global nexthop via 10.0.1.1 dev sta1-eth1")
    sta1.cmd("ip route add default scope global nexthop via 10.0.1.0 dev sta1-wlan0")
    sta2.cmd("ip route del default scope global nexthop via 10.0.2.1 dev sta2-eth1")
    sta2.cmd("ip route add default scope global nexthop via 10.0.2.0 dev sta2-wlan0")
    sta3.cmd("ip route del default scope global nexthop via 10.0.3.1 dev sta3-eth1")
    sta3.cmd("ip route add default scope global nexthop via 10.0.3.0 dev sta3-wlan0")

    time.sleep(89)

    print "*** Stopping D-ITG Server on host ***"
    info('Killing D-ITG server...\n')
    host.cmdPrint('kill $PID')

    print "*** Data processing ***"
    for i in range(1, 4):
        for j in range(0, 1):
            ip = '10.0.'+str(i)+'.'+str(j)
            out_f = folderName+'/sta'+str(i)+'-wlan'+str(j)+'_sptcp.stat'
            nodes['sta'+str(i)].cmd('tshark -r '+folderName+'/sta'+str(i)+'-wlan'+str(j)+'.pcap -qz \"io,stat,0,BYTES()ip.src=='+ip+',AVG(tcp.analysis.ack_rtt)tcp.analysis.ack_rtt&&ip.addr=='+ip+'\" >'+out_f)
        for j in range(1, 2):
            ip = '10.0.'+str(i)+'.'+str(j)
            out_f = folderName+'/sta'+str(i)+'-eth'+str(j)+'_sptcp.stat'
            nodes['sta'+str(i)].cmd('tshark -r '+folderName+'/sta'+str(i)+'-eth'+str(j)+'.pcap -qz \"io,stat,0,BYTES()ip.src=='+ip+',AVG(tcp.analysis.ack_rtt)tcp.analysis.ack_rtt&&ip.addr=='+ip+'\" >'+out_f)

    # print "***Running CLI"
    # CLI(net)

    print "***Stopping network"
    net.stop()


if __name__ == '__main__':
    print "*** Welcome to the Mininet simulation. ***"
    print "---Please name this testing:"
    name = raw_input()
    setLogLevel('info')
    topology(name)
