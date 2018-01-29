#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import OVSKernelAP
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
from subprocess import call, check_call, check_output
import time


def topology():

    call(["sudo", "sysctl", "-w", "net.mptcp.mptcp_enabled=1"])
    call(["sudo", "modprobe", "mptcp_coupled"])
    call(["sudo", "sysctl", "-w", "net.ipv4.tcp_congestion_control=lia"])

    net = Mininet(controller=None, accessPoint=OVSKernelAP, link=TCLink)

    print "***Creating nodes..."
    h1 = net.addHost('h1', mac='00:00:00:00:00:01', ip='10.0.0.1/8')
    s1 = net.addSwitch('s1', mac='00:00:00:00:00:02')
    s2 = net.addSwitch('s2', mac='00:00:00:00:00:03')
    sta1 = net.addStation('sta1')
    sta5 = net.addStation('sta5')
    sta2 = net.addStation('sta2', position='160,90,0')        # for congestion
    sta3 = net.addStation('sta3', position='140,115,0')       # for congestion
    sta4 = net.addStation('sta4', position='150,130,0')         # for congestion
    ap2 = net.addAccessPoint('ap2', ssid='ap2-ssid', mode='g', channel='1', position='150,100,0', range='40')

    print "***Configuring propagation model..."
    net.propagationModel(model="logDistance", exp=4)

    print "***Configuring wifi nodes..."
    net.configureWifiNodes()

    print "***Associating and Creating links..."
    net.addLink(sta1, s2)
    net.addLink(sta5, s2)
    net.addLink(s1, h1)
    net.addLink(s2, s1, bw=1, delay='250ms', loss=1, use_htb=True)
    net.addLink(ap2, s1, bw=1, delay='10ms', loss=1, use_htb=True)
    net.addLink(sta2, ap2)          # for congestion
    net.addLink(sta3, ap2)          # for congestion
    net.addLink(sta4, ap2)          # for congestion

    net.plotGraph(max_x=220, max_y=180)

    net.startMobility(time=0, AC='ssf')
    net.mobility(sta1, 'start', time=60, position='100,50,0')
    net.mobility(sta5, 'start', time=60, position='101,51,0')
    net.mobility(sta1, 'stop', time=70, position='145,100,0')
    net.mobility(sta5, 'stop', time=70, position='146,101,0')
    net.stopMobility(time=130)

    print "***Starting network"
    net.start()

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

    '''for congestion'''
    sta2.cmd('ifconfig sta2-wlan0 10.0.2.0/32')
    sta2.cmd('ip rule add from 10.0.2.0 table 1')
    sta2.cmd('ip route add 10.0.2.0/32 dev sta2-wlan0 scope link table 1')
    sta2.cmd('ip route add default via 10.0.2.0 dev sta2-wlan0 table 1')
    sta2.cmd('ip route add default scope global nexthop via 10.0.2.0 dev sta2-wlan0')

    sta3.cmd('ifconfig sta3-wlan0 10.0.3.0/32')
    sta3.cmd('ip rule add from 10.0.3.0 table 1')
    sta3.cmd('ip route add 10.0.3.0/32 dev sta3-wlan0 scope link table 1')
    sta3.cmd('ip route add default via 10.0.3.0 dev sta3-wlan0 table 1')
    sta3.cmd('ip route add default scope global nexthop via 10.0.3.0 dev sta3-wlan0')

    sta4.cmd('ifconfig sta4-wlan0 10.0.4.0/32')
    sta4.cmd('ip rule add from 10.0.4.0 table 1')
    sta4.cmd('ip route add 10.0.4.0/32 dev sta4-wlan0 scope link table 1')
    sta4.cmd('ip route add default via 10.0.4.0 dev sta4-wlan0 table 1')
    sta4.cmd('ip route add default scope global nexthop via 10.0.4.0 dev sta4-wlan0')

    sta5.cmd('ifconfig sta5-wlan0 10.0.5.0/32')
    sta5.cmd('ifconfig sta5-eth1 10.0.5.1/32')
    sta5.cmd('ip rule add from 10.0.5.0 table 1')
    sta5.cmd('ip rule add from 10.0.5.1 table 2')
    sta5.cmd('ip route add 10.0.5.0/32 dev sta5-wlan0 scope link table 1')
    sta5.cmd('ip route add default via 10.0.5.0 dev sta5-wlan0 table 1')
    sta5.cmd('ip route add 10.0.5.1/32 dev sta5-eth1 scope link table 2')
    sta5.cmd('ip route add default via 10.0.5.1 dev sta5-eth1 table 2')
    sta5.cmd('ip route add default scope global nexthop via 10.0.5.1 dev sta5-eth1')

    print "***Setting flow tables..."
    call(["sudo", "bash", "flowTable/ew-ftConfig.sh"])

    sta1.cmdPrint("ip link set dev sta1-wlan0 multipath off")
    sta5.cmdPrint("ip link set dev sta5-wlan0 multipath off")

    print "***Starting iperf and tcpdump..."
    h1.cmd("iperf -s &")
    sta1.cmd("iperf -c 10.0.0.1 -t 130 &")
    sta2.cmd("iperf -c 10.0.0.1 -t 130 &")                            # for congestion
    sta3.cmd("iperf -c 10.0.0.1 -t 130 &")                            # for congestion
    sta4.cmd("iperf -c 10.0.0.1 -t 130 &")                            # for congestion
    sta5.cmd("iperf -c 10.0.0.1 -t 130 &")                            # for congestion

    h1.cmd("tcpdump -i h1-eth0 -w h1-eth0-ew-multi-congest.pcap &")
    # sta1.cmd("tcpdump -i any -w sta1-ew-multi.pcap &")

    time.sleep(65)
    sta1.cmd("ip link set dev sta1-wlan0 multipath on")
    sta5.cmd("ip link set dev sta5-wlan0 multipath on")
    # print "***Resetting the flow table again..."
    # call(["sudo", "ovs-ofctl", "del-flows", "s1"])
    # call(["sudo", "ovs-ofctl", "del-flows", "s2"])
    # call(["sudo", "ovs-ofctl", "del-flows", "ap2"])
    # call(["sudo", "bash", "ftConfig.sh"])

    time.sleep(65)

    print "***Running CLI"
    CLI(net)

    print "***Stopping network"
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
