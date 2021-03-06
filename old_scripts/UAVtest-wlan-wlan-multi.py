#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, OVSKernelAP
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
from subprocess import call, check_call, check_output
import time, datetime


def topology():

    # call(["sudo", "sysctl", "-w", "net.mptcp.mptcp_enabled=1"])
    # call(["sudo", "modprobe", "mptcp_coupled"])
    # call(["sudo", "sysctl", "-w", "net.ipv4.tcp_congestion_control=lia"])

    net = Mininet(controller=Controller, accessPoint=OVSKernelAP, link=TCLink)

    print "***Creating nodes..."
    h1 = net.addHost('h1', mac='00:00:00:00:00:01', ip='10.0.0.1/8')
    s1 = net.addSwitch('s1', mac='00:00:00:00:00:02')
    s2 = net.addSwitch('s2', mac='00:00:00:00:00:03')
    sta1 = net.addStation('sta1')
    # ap1 = net.addAccessPoint('ap-sat', ssid='ap-sat-ssid', mode='n', channel='1',
    #                          position='100,100,0', range='200')
    ap2 = net.addAccessPoint('ap2', ssid='ap2-ssid', mode='g', channel='1', position='150,100,0', range='40')
    # ap3 = net.addAccessPoint('ap3', ssid='ap3-ssid', mode='g', channel='1',
    #                          position='130,50,0', range='40')
    c1 = net.addController('c1', controller=Controller)

    print "***Configuring propagation model..."
    net.propagationModel(model="logDistance", exp=4)

    print "***Configuring wifi nodes..."
    net.configureWifiNodes()

    print "***Associating and Creating links..."
    net.addLink(sta1, s2)
    net.addLink(s1, h1)
    net.addLink(s2, s1, bw=1, delay='250ms', loss=1, use_htb=True)
    # net.addLink(ap1, s1)
    net.addLink(ap2, s1, bw=1, delay='10ms', loss=1, use_htb=True)
    # net.addLink(ap3, s1)

    net.plotGraph(max_x=220, max_y=180)

    net.startMobility(time=0, AC='ssf')
    net.mobility(sta1, 'start', time=30, position='100,50,0')
    net.mobility(sta1, 'stop', time=40, position='145,100,0')
    net.stopMobility(time=70)

    print "***Starting network"
    net.start()
    # net.build()
    # c1.start()
    # s1.start([c1])
    # s2.start([c1])
    # ap1.start([c1])
    # ap2.start([c1])
    # ap3.start([c1])

    print "***Addressing for station..."
    # sta1.setIP('10.0.0.3/8', intf="sta1-wlan0")

    sta1.cmd('ifconfig sta1-wlan0 10.0.1.0/32')
    sta1.cmd('ifconfig sta1-eth1 10.0.1.1/32')

    sta1.cmd('ip rule add from 10.0.1.0 table 1')
    sta1.cmd('ip rule add from 10.0.1.1 table 2')

    sta1.cmd('ip route add 10.0.1.0/32 dev sta1-wlan0 scope link table 1')
    sta1.cmd('ip route add default via 10.0.1.0 dev sta1-wlan0 table 1')

    sta1.cmd('ip route add 10.0.1.1/32 dev sta1-eth1 scope link table 2')
    sta1.cmd('ip route add default via 10.0.1.1 dev sta1-eth1 table 2')

    sta1.cmd('ip route add default scope global nexthop via 10.0.1.1 dev sta1-eth1')

    print "***Setting flow tables..."
    call(["sudo", "bash", "ftConfig.sh"])

    print "***Starting iperf and tcpdump..."
    h1.cmd("iperf -s &")
    sta1.cmd("iperf -c 10.0.0.1 -t 130 &")

    h1.cmd("tcpdump -i h1-eth0 -w h1-eth0-multi.pcap &")
    sta1.cmd("tcpdump -i any -w sta1-multi.pcap &")

    # time.sleep(35)
    # print "***Resetting the flow table again..."
    # call(["sudo", "ovs-ofctl", "del-flows", "s1"])
    # call(["sudo", "ovs-ofctl", "del-flows", "s2"])
    # call(["sudo", "ovs-ofctl", "del-flows", "ap2"])
    # call(["sudo", "bash", "ftConfig.sh"])

    print "***Running CLI"
    CLI(net)

    # time.sleep(70)

    print "***Stopping network"
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
