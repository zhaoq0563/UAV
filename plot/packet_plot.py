#!/usr/bin/python

import sys, os
import numpy as np
import matplotlib.pyplot as plt

def getStat(dir, senderNumber, protocol):
    t, d, b = ([] for i in range(3))
    for i in range(1, senderNumber+1):
        ethfname = dir+'sta'+str(i)+'-eth1_'+protocol+'.stat'
        wlanfname = dir + 'sta' + str(i) + '-wlan0_'+protocol+'.stat'
        throughtput, delay, byte = (0.0, 0.0, 0.0)

        if os.path.isfile(ethfname):
            f1 = open(ethfname, 'r')
            for line in f1:
                if line.startswith('|'):
                    l = line.strip().strip('|').split()
                    if '<>' in l:
                        duration = float(l[2])
                        byte += float(l[8])
                        if duration!=0:
                            throughtput += float(l[8])*8/(duration*10**6)
                        delay += byte*float(l[10])
            f1.close()
        if os.path.isfile(wlanfname):
            f2 = open(wlanfname, 'r')
            for line in f2:
                if line.startswith('|'):
                    l = line.strip().strip('|').split()
                    if '<>' in l:
                        duration = float(l[2])
                        byte += float(l[8])
                        if duration!=0:
                            throughtput += float(l[8])*8/(duration*10**6)
                        delay += byte*float(l[10])
            f2.close()
        if byte!=0:
            delay /= byte
        else:
            delay = 0.0

        t.append(throughtput)
        d.append(delay)
        b.append(byte)

    return t, d, b


if __name__ == '__main__':
    senderNumber = int(sys.argv[1])
    name = sys.argv[2]
    currentdir = os.getcwd()

    FDM_goodput, FDM_delay, FDM_byte = getStat(currentdir + "/../pcap_" + name + "-fdm/", senderNumber, 'mptcp')
    print(FDM_goodput, FDM_delay)

    multi_goodput, multi_delay, multi_byte = getStat(currentdir + "/../pcap_" + name + "-mptcp/", senderNumber, 'mptcp')
    print(multi_goodput, multi_delay)

    single_goodput, single_delay, single_byte = getStat(currentdir + "/../pcap_" + name + "-sptcp/", senderNumber, 'sptcp')
    print(single_goodput, single_delay)

    n_groups = len(FDM_goodput)

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15, 5))
    ax = axes[0, 0]
    ax2 = axes[0, 1]
    index = np.arange(n_groups) * 2
    bar_width = 0.35

    opacity = 0.4
    error_config = {'ecolor': '0.3'}

    rects1 = ax.bar(index, FDM_goodput, bar_width,
                    alpha=opacity, color='b', edgecolor="none",
                    label='FDM')
    rects2 = ax.bar(index + bar_width, multi_goodput, bar_width,
                    alpha=opacity, color='r', edgecolor="none",
                    label='MPTCP')
    rects3 = ax.bar(index + 2 * bar_width, single_goodput, bar_width,
                    alpha=opacity, color='g', edgecolor="none",
                    label='SPTCP')

    ax.set_xlabel('Hosts')
    ax.set_ylabel('Throughput (Mbps)')
    ax.set_title('Throughput performance')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels([str(i) for i in range(30)])
    ax.legend(loc='best', fontsize=12)
    ax.set_ylim([0, 0.8])

    rects1 = ax2.bar(index, FDM_delay, bar_width,
                     alpha=opacity, color='b', edgecolor="none",
                     label='FDM')
    rects2 = ax2.bar(index + bar_width, multi_delay, bar_width,
                     alpha=opacity, color='r', edgecolor="none",
                     label='MPTCP')
    rects3 = ax2.bar(index + 2 * bar_width, single_delay, bar_width,
                     alpha=opacity, color='g', edgecolor="none",
                     label='SPTCP')
    ax2.set_xlabel('Hosts')
    ax2.set_ylabel('Packet delay (s)')
    ax2.set_title('Delay performance')
    ax2.set_xticks(index + bar_width / 2)
    ax2.set_xticklabels([str(i) for i in range(30)])
    ax2.legend(loc='best', fontsize=12)

    pkt_rate = [np.sum(FDM_goodput)/senderNumber, np.sum(multi_goodput)/senderNumber,
                np.sum(single_goodput)/senderNumber]
    ax3 = axes[1, 0]
    ax4 = axes[1, 1]
    index = np.arange(3)
    ax3.scatter(index, pkt_rate, marker='*', s=50)
    ax3.set_xlabel('Protocols')
    ax3.set_ylabel('Average Throughput (Mbps)')
    ax3.set_xticks(index)
    ax3.set_ylim([0, 0.5])
    ax3.set_xticklabels(["FDM", "MPTCP", "SPTCP"])

    avg_delay = [np.sum(FDM_delay)/senderNumber, np.sum(multi_delay)/senderNumber, np.sum(single_delay)/senderNumber]
    index = np.arange(3)
    ax4.scatter(index, avg_delay, marker="o", s=50)
    ax4.set_xlabel('Protocols')
    ax4.set_ylabel('Average Delay (Sec)')
    ax4.set_xticks(index)
    ax4.set_xticklabels(["FDM", "MPTCP", "SPTCP"])
    # ax4.set_yscale("log")
    ax4.set_ylim([0, 0.2])
    fig.tight_layout()
    plt.show()