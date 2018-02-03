#!/usr/bin/python

from subprocess import call, check_call, check_output
from mininet.net import Mininet
from mininet.node import Node, OVSKernelSwitch, Host, RemoteController, UserSwitch, Controller
from mininet.link import Link, Intf, TCLink, TCULink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from functools import partial
import sys, time
flush=sys.stdout.flush
import os.path, string
from threading import Thread
from subprocess import call, check_call, check_output
import datetime
import collections

class ServerSetup(Thread):
    def __init__(self, node, name):
        "Constructor"
        Thread.__init__(self)
        self.node = node
        self.name = name

    def run(self):
        print("Server set up for iperf " + self.name)
        self.node.cmdPrint("iperf -s")

    def close(self, i):
        self.running = False
        print("exit " + self.name)


def WifiNet(inputFile, mptcp):

    # enable mptcp
    mptcp_option="net.mptcp.mptcp_enabled="+str(mptcp)
    call(["sudo", "sysctl","-w",mptcp_option])
    call(["sudo", "modprobe","mptcp_coupled"])
    call(["sudo", "sysctl","-w", "net.ipv4.tcp_congestion_control=cubic"])

    input = open(inputFile, "r")
    """ Node names """
    max_outgoing = []
    hosts = []
    switches = []  # satellite and dummy satellite
    links = []

    queueConfig = open("FDMQueueConfig.sh", "w")
    flowTableConfig = open("FDMFlowTableConfig.sh", "w")
    queueConfig.write("#!/bin/bash\n\n")
    flowTableConfig.write("#!/bin/bash\n\n")
    queue_num = 1
    num_host = 0
    num_ship = 0
    num_sat = 0

    # Read src-des pair for testing
    src_hosts = []
    des_hosts = []
    src_dest = {}
    des_ip = []
    line = input.readline()
    while line.strip() != "End":
        src, des, ip = line.strip().split()
        src_hosts.append(int(src.lstrip('host')))
        des_hosts.append(int(des.lstrip('host')))
        src_dest[int(src.lstrip('host'))]=int(des.lstrip('host'))
        des_ip.append(ip)
        line = input.readline()

    # Add nodes
    # Mirror ships are switches
    line = input.readline()
    while line.strip() != "End":
        action, type_node, target = line.strip().split()
        if type_node == "host:":
            hosts.append(target)
            num_host += 1
        else:
            if type_node == "ship:":
                num_ship += 1
                max_outgoing.append(0)
            elif type_node == "hub:":
                num_sat += 1
            switches.append(target)
        line = input.readline()

    # Add links
    line = input.readline()
    while line.strip() != "End":
        action, type_node, end1, end2, bw, delay = line.strip().split()
        if end1[0] == "s" and int(end1[1:]) <= num_ship and end2[0] == "s":
            max_outgoing[int(end1[1:]) - 1] += 1
        links.append([end1, end2, bw, delay])
        line = input.readline()

    #print(max_outgoing)
    # Routing table of hosts
    line = input.readline()
    while line.strip() != "End":
        host, st, num_ip = line.strip().split()
        file = open(host + ".sh", "w")
        file.write("#!/bin/bash\n\n")
        for i in range(0, int(num_ip)):
            ipaddr = input.readline().strip()
            intf = host + "-eth" + str(i)
            file.write("ifconfig " + intf + " " + ipaddr + " netmask 255.255.255.255\n")
            file.write("ip rule add from " + ipaddr + " table " + str(i + 1) + "\n")
            file.write("ip route add " + ipaddr + "/32 dev " + intf + " scope link table " + str(i + 1) + "\n")
            file.write("ip route add default via " + ipaddr + " dev " + intf + " table " + str(i + 1) + "\n")
            if i == 0:
                file.write("ip route add default scope global nexthop via " + ipaddr + " dev " + intf + "\n")
        file.close()
        call(["sudo", "chmod", "777", host + ".sh"])
        line = input.readline()

    # Flow table and queue
    queue_num = 1
    host_eth={}
    bwReq=[]
    line = input.readline()
    while line:
        # print(line)
        end1, end2, num_flow = line.strip().split()
        num_flow = num_flow.strip().split(":")[1]

        # Routing tables have been configured
        if "host" in end1:
            #print(line)
            flow = 0
            host_eth[int(end1.split('-')[0].lstrip('host'))]=int(num_flow)
            for i in range(0, int(num_flow)):
                line = input.readline()
                flow += float(line.strip().split()[1])
            bwReq.append(flow)
        else:
            switch, intf = end1.split("-")
            index_switch = int(switch[1:])
            index_intf = intf[3:]

            if index_switch <= num_ship and "host" != end2[0:4]:
                # uplink to ship, need to configure both flowtable and queue

                # Set queue size to one to enable packet drop
                commandQueue = "sudo ifconfig " + end1 + " txqueuelen 20"
                #queueConfig.write(commandQueue + "\n")

                # put the queues for one port on one line in definition
                commandQueue = "sudo ovs-vsctl -- set Port " + end1 + " qos=@newqos -- --id=@newqos create QoS type=linux-htb other-config:max-rate=100000000 "
                queue_nums = []
                rates = []
                ipaddrs = []
                for i in range(0, int(num_flow) - 1):
                    ipaddr, rate = input.readline().strip().split()
                    rates.append(rate)
                    ipaddrs.append(ipaddr)
                    queue_nums.append(queue_num)
                    commandQueue += "queues:" + str(queue_num) + "=@q" + str(queue_num) + " "
                    queue_num += 1
                ipaddr, rate = input.readline().strip().split()
                rates.append(rate)
                ipaddrs.append(ipaddr)
                queue_nums.append(queue_num)
                commandQueue += "queues:" + str(queue_num) + "=@q" + str(queue_num) + " -- "
                queue_num += 1

                for i in range(0, int(num_flow) - 1):
                    commandQueue += " --id=@q" + str(queue_nums[i]) + " create Queue other-config:min-rate=" + str(int(float(rates[i]) * 1000000)) + " other-config:max-rate=" + str(int(float(rates[i]) * 1000000)) + " -- "
                commandQueue += " --id=@q" + str(queue_nums[len(queue_nums) - 1]) + " create Queue other-config:min-rate=" + str(int(float(rates[len(queue_nums) - 1]) * 1000000)) + " other-config:max-rate=" + str(int(float(rates[len(queue_nums) - 1]) * 1000000))
                queueConfig.write(commandQueue + "\n")

                for i in range(0, int(num_flow)):
                    commandFlowTable = "sudo ovs-ofctl add-flow " + switch + " ip,nw_src=" + ipaddrs[i] + "/32,actions=set_queue:" + str(queue_nums[i]) + ",output:" + index_intf
                    flowTableConfig.write(commandFlowTable + "\n")

                commandFlowTable = "sudo ovs-ofctl add-flow " + switch + " in_port=" + index_intf + ",actions=normal"
                flowTableConfig.write(commandFlowTable + "\n")
            elif index_switch <= num_ship:
                # ship to host downlink
                # port forwarding
                for i in range(0, int(num_flow)):
                    input.readline()
                for i in range(0, int(max_outgoing[index_switch - 1])):
                    # ipaddr, rate = input.readline().strip().split()
                    commandFlowTable = "sudo ovs-ofctl add-flow " + switch + " in_port=" + str(int(index_intf) - i - 1) + ",actions=output:" + index_intf
                    flowTableConfig.write(commandFlowTable + "\n")
                commandFlowTable = "sudo ovs-ofctl add-flow " + switch + " in_port=" + index_intf + ",actions=normal"
                flowTableConfig.write(commandFlowTable + "\n")

            elif index_switch <= num_ship + num_sat * 2:
                # sat-hub-dummy_sat
                # port forwarding
                for i in range(0, int(num_flow)):
                    input.readline()
                for i in range(1, int(index_intf)):
                    commandFlowTable = "sudo ovs-ofctl add-flow " + switch + " in_port=" + str(i) + ",actions=output:" + index_intf
                    flowTableConfig.write(commandFlowTable + "\n")
                commandFlowTable = "sudo ovs-ofctl add-flow " + switch + " in_port=" + index_intf + ",actions=normal"
                flowTableConfig.write(commandFlowTable + "\n")
            elif index_switch <= num_ship + num_sat * 3:
                # dummy to mirror ship, ip forwarding
                for i in range(0, int(num_flow)):
                    ipaddr, rate = input.readline().strip().split()
                    commandFlowTable = "sudo ovs-ofctl add-flow " + switch + " ip,nw_src=" + ipaddr + "/32,actions=output:" + index_intf
                    flowTableConfig.write(commandFlowTable + "\n")
                commandFlowTable = "sudo ovs-ofctl add-flow " + switch + " in_port=" + index_intf + ",actions=normal"
                flowTableConfig.write(commandFlowTable + "\n")
            else:
                # mirror ship to host, port forwarding
                for i in range(0, int(num_flow)):
                    input.readline()
                for i in range(1, int(index_intf)):
                    commandFlowTable = "sudo ovs-ofctl add-flow " + switch + " in_port=" + str(i) + ",actions=output:" + index_intf
                    flowTableConfig.write(commandFlowTable + "\n")
                commandFlowTable = "sudo ovs-ofctl add-flow " + switch + " in_port=" + index_intf + ",actions=normal"
                flowTableConfig.write(commandFlowTable + "\n")
        line = input.readline()
    for i in range(0, num_ship):
        queueConfig.write("sudo ovs-ofctl -O Openflow13 queue-stats s" + str(i + 1) + "\n")

    for i in range(0, num_ship + 3 * num_sat):
        flowTableConfig.write("sudo ovs-ofctl add-flow s" + str(i + 1) + " priority=100,actions=normal\n")

    flowTableConfig.close()
    queueConfig.close()
    call(["sudo", "chmod", "777", "FDMQueueConfig.sh"])
    call(["sudo", "chmod", "777", "FDMFlowTableConfig.sh"])
    #print(host_eth)
    net = Mininet(link=TCLink, controller=None, autoSetMacs = True)

    nodes = {}

    """ Initialize Ships """
    for host in hosts:
        node = net.addHost(host)
        nodes[host] = node

    """ Initialize SATCOMs """
    for switch in switches:
        node = net.addSwitch(switch)
        nodes[switch] = node

    """ Add links """
    for link in links:
        name1, name2, b, d = link[0], link[1], link[2], link[3]
        node1, node2 = nodes[name1], nodes[name2]
        if(d != '0'):
            net.addLink(node1, node2, bw=float(b), delay=d+'ms')
        else:
            net.addLink(node1, node2)

    """ Start the simulation """
    info('*** Starting network ***\n')
    net.start()

    #  set all ships
    for i in range(0,num_host):
    #for i in range(0,0):
        src=nodes[hosts[i]]
        info("--configing routing table of "+hosts[i])
        if os.path.isfile(hosts[i]+'.sh'):
            src.cmdPrint('./'+hosts[i]+'.sh')

    time.sleep(3)
    info('*** set queues ***\n')
    call(["sudo", "bash","FDMQueueConfig.sh"])

    time.sleep(3)
    info('*** set flow tables ***\n')
    call(["sudo", "bash","FDMFlowTableConfig.sh"])

    # info('*** start test ping and iperf***\n')
    #
    # myServer = []
    # des_open = []
    # for i in range(0,len(src_hosts)):
    #     src = nodes[src_hosts[i]]
    #     des = nodes[des_hosts[i]]
    #     myServer.append("")
    #     des_open.append(False)
    #     if des.waiting == False:
    #         info("Setting up server " + des_hosts[i] + " for iperf",'\n')
    #         myServer[i] = ServerSetup(des, des_hosts[i])
    #         myServer[i].setDaemon(True)
    #         myServer[i].start()
    #         des_open[i] = True
    #         time.sleep(1)
    #
    # for i in range(0,len(src_hosts)):
    #     src = nodes[src_hosts[i]]
    #     des = nodes[des_hosts[i]]
    #     info("testing",src_hosts[i],"<->",des_hosts[i],'\n')
    #     src.cmdPrint('ping -c 2 ' + des_ip[i])
    #     time.sleep(0.2)
    #     src.cmdPrint('iperf -c ' + des_ip[i] + ' -t 3 -i 1')
    #     time.sleep(0.2)
    #
    # time.sleep(10)
    # for i in range(0,len(src_hosts)):
    #     if des_open[i] == True:
    #         print("Closing iperf session " + des_hosts[i])
    #         myServer[i].close(i)
    #
    # time.sleep(5)
    # start D-ITG Servers


    # start D-ITG application
    # set simulation time
    keys=src_dest.keys()
    keys.sort()
    senderList, recvList=([] for i in range(2))
    for key in keys:
        senderList.append(key)
        recvList.append(src_dest[key])
    print(src_dest)
    print(senderList,recvList)
    dests = list(set(recvList))
    for i in range(0,1):
        for i in dests:
            srv = nodes[hosts[i]]
            info("starting D-ITG servers...\n")
            srv.cmdPrint("cd ~/D-ITG-2.8.1-r1023/bin")
            srv.cmdPrint("./ITGRecv &")
            srv.cmdPrint("PID=$!")
            time.sleep(0.2)

        time.sleep(1)
        sTime = 60000# default 120,000ms
        for i in range(0,len(senderList)):
            # normal requirement
            #senderList = [0,1,3,4,6,7,9,10,12,13]
            #recvList = [11,14,2,8,5,11,5,8,2,11]
            #bwReq = [6,4,7,3,4,4,3,3,3,3]

            # large requirement
            #bwReq = [2,12,3,3,5,5,12,2,12,2]
            ITGTest(senderList[i], recvList[i], hosts, nodes, bwReq[i]*125, sTime)
            srv=nodes[hosts[senderList[i]]]
            for j in range(0,host_eth[senderList[i]]):
                srv.cmdPrint("tcpdump -i host"+str(senderList[i])+"-eth"+str(j)+" -w host"+str(senderList[i])+"eth"+str(j)+".pcap &")
            time.sleep(0.2)
        info("running simulaiton...\n")
        info("please wait...\n")

        time.sleep(sTime/1000+10)
        for i in dests:
            srv=nodes[hosts[i]]
            info("killing D-ITG servers...\n")

            srv.cmdPrint("kill $PID")
        for i in range(0,len(senderList)):
            srv=nodes[hosts[senderList[i]]]
            for j in range(host_eth[senderList[i]]-1,-1,-1):
                ip="10.0."+str(senderList[i]+1)+"."+str(j)
                out_f="host"+str(senderList[i])+"eth"+str(host_eth[senderList[i]]-1-j)+".stat"
                srv.cmdPrint("tshark -r host"+str(senderList[i])+"eth"+str(host_eth[senderList[i]]-1-j)+".pcap -qz \"io,stat,0,BYTES()ip.src=="+ip+",AVG(tcp.analysis.ack_rtt)tcp.analysis.ack_rtt&&ip.addr=="+ip+"\" >"+out_f)
        Analysis(senderList, recvList)

        # You need to change the path here
        #call(["sudo", "python","analysis.py"])
    #CLI(net)

    net.stop()
    info('*** net.stop()\n')

def ITGTest(srcNo, dstNo, hosts, nodes, bw, sTime):
    src = nodes[hosts[srcNo]]
    dst = nodes[hosts[dstNo]]
    info("Sending message from ",src.name,"<->",dst.name,"...",'\n')
    src.cmdPrint("cd ~/D-ITG-2.8.1-r1023/bin")
    src.cmdPrint("./ITGSend -T TCP  -a 10.0.0."+str(dstNo+1)+" -c 1000 -C "+str(bw)+" -t "+str(sTime)+" -l sender"+str(srcNo)+".log -x receiver"+str(srcNo)+"ss"+str(dstNo)+".log &")

def extractStat(sndList, recvList):
    '''
        Extract statistic information from log files
    '''
    # decode of sender files
    for i in range(0, len(sndList)):
        initialFileName = "sender" + str(sndList[i]) + ".log"
        decodedSenderFile = "sender" + str(sndList[i]) + ".txt"
        os.system("./ITGDec " + str(initialFileName) + " > " + str(decodedSenderFile))

    # decode of receiver files
    for i in range(0, len(sndList)):
        initialFileName = "receiver" + str(sndList[i]) + "ss" + str(recvList[i]) + ".log"
        decodedRecvFile = "receiver" + str(sndList[i]) + "ss" + str(recvList[i]) + ".txt"
        os.system("./ITGDec " + str(initialFileName) + " > " + str(decodedRecvFile))


def statAnalysis(sndList, recvList):
    '''
        Analysis the decoded files
    '''
    time = datetime.datetime.now()
    fileName = "result_" + str(time) + ".csv"
    g = open("/home/momo/FDMTestBed/testcase4/FDM/" + fileName, "w")
    str_ini = 'host,'

    # sender host list
    for i in range(0,len(sndList)):
        str_ini = str_ini + "host" + str(sndList[i])
        if(i < len(sndList) - 1):
            str_ini = str_ini + ','
        else:
            str_ini = str_ini + '\n'

    # initial values
    total_time = 'total_time,'
    total_packets = 'total_packets,'
    min_delay = 'min_delay,'
    max_delay = 'max_delay,'
    avg_delay = 'avg_delay,'
    avg_jitter = 'avg_jitter,'
    sd_delay = 'sd_delay,'
    avg_bit_rate = 'avg_bit_rate,'
    avg_pkt_rate = 'avg_pkt_rate,'

    for i in range(0, len(sndList)):
        decodedRecvFile = "receiver" + str(sndList[i]) + "ss" + str(recvList[i]) + ".txt"
        flag = 0
        f = open(decodedRecvFile,"r")
        if(i < len(sndList) - 1):
            str_split = ","
        else:
            str_split = '\n'

        # read separate files
        while 1:
            line = f.readline()

            if not line:
                break

            if(line.find("TOTAL RESULTS") != -1):
                flag = 1

            total_time = findnSeek(flag, line, "Total time", total_time, str_split)
            total_packets = findnSeek(flag, line,"Total packets", total_packets, str_split)
            min_delay = findnSeek(flag, line, "Minimum delay", min_delay, str_split)
            max_delay = findnSeek(flag, line, "Maximum delay", max_delay, str_split)
            avg_delay = findnSeek(flag, line, "Average delay", avg_delay, str_split)
            avg_jitter = findnSeek(flag, line, "Average jitter", avg_jitter, str_split)
            sd_delay = findnSeek(flag, line, "Delay standard", sd_delay, str_split)
            avg_bit_rate = findnSeek(flag, line, "Average bitrate", avg_bit_rate, str_split)
            avg_pkt_rate = findnSeek(flag, line, "Average packet", avg_pkt_rate, str_split)

    # write results to files
    g.write(str_ini)
    g.write(total_time)
    g.write(total_packets)
    g.write(min_delay)
    g.write(max_delay)
    g.write(avg_delay)
    g.write(avg_jitter)
    g.write(sd_delay)
    g.write(avg_bit_rate)
    g.write(avg_pkt_rate)
    g.close()

def findnSeek(flag, line, findStr,result, str_split):
    if (flag == 1 and line.find(findStr) != -1):
        result = result + line.split('=')[1].strip().split(" ")[0]
        result = result + str_split
        return(result)
    else:
        result = result + '' # do nothing
        return(result)


def Analysis(sndList, recvList):
    os.chdir("/home/momo/D-ITG-2.8.1-r1023/bin/")
    extractStat(sndList, recvList)
    statAnalysis(sndList, recvList)

if __name__ == '__main__':
    setLogLevel('info')

    testTimes = 1
    for i in range(0, testTimes):
        #WifiNet("all_4.txt")
        WifiNet("all_large.txt",1)
        os.chdir("/home/momo/FDMTestBed/testcase4/FDM")
        WifiNet("all_large_nofdm.txt",1)
        os.chdir("/home/momo/FDMTestBed/testcase4/FDM")
        WifiNet("all_large_nofdm.txt",0)
