import os
from numpy import array
import numpy as np
import matplotlib.pyplot as plt


def getStat(dir):
    cnt = 0
    tot_time=[]
    tot_packet=[]
    tot_delay=[]
    tot_jitter=[]
    for file in os.listdir(dir):
        cnt += 1
        time, packet, delay, jitter = ([] for i in range(4))
        f = open(dir+file,'r')
        for line in f:
            l=line.split(",")
            if("time" in l[0]):
                time = [float(i) for i in l[1:]]
            elif("packet" in l[0]):
                packet = [float(i) for i in l[1:]]
            elif("avg_delay" in l[0]):
                delay = [float(i)*j for i,j in zip(l[1:], packet)]
            elif("jitter" in l[0]):
                jitter = [float(i) for i in l[1:]]
        if(len(tot_time)==0):
            tot_time=time
            tot_packet=packet
            tot_delay=delay
            tot_jitter=jitter
        else:
            tot_time=[i+j for i,j in zip(tot_time,time)]
            tot_packet=[i+j for i,j in zip(tot_packet,packet)]
            tot_delay=[i+j for i,j in zip(tot_delay,delay)]
            tot_jitter=[i+j for i,j in zip(tot_jitter,jitter)]
    t=array(tot_time)
    p=array(tot_packet)
    d=array(tot_delay)
    j=array(tot_jitter)
    return t,p,d,j,cnt






if __name__ == '__main__':
    currentdir=os.getcwd()
    #req=array([6,4,7,3,4,4,3,3,3,3])*1000000
    req=array([0.814540000000000,	0.852264000000000,	0.635661000000000,	0.443964000000000,\
         0.866750000000000,	0.355074000000000,	0.224171000000000,	0.604991000000000,\
         0.142187000000000,	0.421112000000000,	0.725775000000000,	0.734230000000000,\
         0.176855000000000,	0.265322000000000,	0.223770000000000,	0.0875000000000000,	0.180617000000000,\
         0.723173000000000	,0.660617000000000,	0.627347000000000,	0.910570000000000,	0.745847000000000	,0.383306000000000,\
         0.575495000000000,	0.275070000000000,	0.451639000000000,	0.804450000000000,	0.0299920000000000,\
         0.0870770000000000,	0.989145000000000])*1000000
    FDM_t, FDM_p, FDM_d, FDM_j, cnt = getStat(currentdir+"/"+"FDM/")
    FDM_goodput=np.divide(FDM_p*8000,FDM_t)
    FDM_delay=np.divide(FDM_d,FDM_p)
    print(FDM_goodput, FDM_delay)

    multi_t, multi_p, multi_d, multi_j, cnt = getStat(currentdir+"/"+"multi/")
    multi_goodput=np.divide(multi_p*8000,multi_t)
    multi_delay=np.divide(multi_d,multi_p)
    print(multi_goodput, multi_delay)

    single_t, single_p, single_d, single_j, cnt = getStat(currentdir+"/"+"single/")
    single_goodput=np.divide(single_p*8000,single_t)
    single_delay=np.divide(single_d,single_p)
    print(single_goodput, single_delay)

    n_groups = len(FDM_goodput)

    fig, axes = plt.subplots(nrows=2,ncols=2, figsize=(15,5))
    ax=axes[0,0]
    ax2=axes[0,1]
    index = np.arange(n_groups)*2
    bar_width = 0.35

    opacity = 0.4
    error_config = {'ecolor': '0.3'}

    rects1 = ax.bar(index, FDM_goodput, bar_width,
                    alpha=opacity, color='b',edgecolor="none",
                    label='FDM')

    rects3 = ax.bar(index, req-FDM_goodput, bar_width,bottom=FDM_goodput,
                    alpha=opacity, color='w', hatch='//', edgecolor="none", linewidth=0,
                    )

    rects2 = ax.bar(index + bar_width, multi_goodput, bar_width,
                    alpha=opacity, color='r',edgecolor="none",
                    label='MPTCP')
    rects3 = ax.bar(index+bar_width, req-multi_goodput, bar_width,bottom=multi_goodput,
                    alpha=opacity, color='w', hatch='//', edgecolor="none", linewidth=0,
                    )
    rects2 = ax.bar(index + 2*bar_width, single_goodput, bar_width,
                    alpha=opacity, color='g',edgecolor="none",
                    label='SPTCP')
    rects3 = ax.bar(index+2*bar_width, req-single_goodput, bar_width,bottom=single_goodput,
                    alpha=opacity, color='w', hatch='//', edgecolor="none", linewidth=0,
                    label='Gap')

    ax.set_xlabel('Hosts')
    ax.set_ylabel('Goodput(bps)')
    ax.set_title('Goodput performance')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels([str(i) for i in range(30)])
    ax.legend(loc='best',fontsize=12)
    ax.set_ylim([0,1500000])

    rects1 = ax2.bar(index, FDM_delay, bar_width,
                    alpha=opacity, color='b',edgecolor="none",
                    label='FDM')
    rects2 = ax2.bar(index + bar_width, multi_delay, bar_width,
                    alpha=opacity, color='r',edgecolor="none",
                    label='MPTCP')
    rects2 = ax2.bar(index + 2*bar_width, single_delay, bar_width,
                    alpha=opacity, color='g',edgecolor="none",
                    label='SPTCP')
    ax2.set_xlabel('Hosts')
    ax2.set_ylabel('Packet delay(Sec)')
    ax2.set_title('Delay performance')
    ax2.set_xticks(index + bar_width / 2)
    ax2.set_xticklabels([str(i) for i in range(30)])
    ax2.legend(loc='best',fontsize=12)

    pkt_rate=[np.sum(FDM_p)*8000/1000000/np.sum(FDM_t),np.sum(multi_p)*8000/1000000/np.sum(multi_t),np.sum(single_p)*8000/1000000/np.sum(single_t) ]
    ax3=axes[1,0]
    ax4=axes[1,1]
    index=np.arange(3)
    ax3.scatter(index,pkt_rate, marker='*', s=50)
    ax3.set_xlabel('Protocols')
    ax3.set_ylabel('Average Goodput (Mbps)')
    ax3.set_xticks(index )
    ax3.set_ylim([0,2])
    ax3.set_xticklabels(["FDM","MPTCP","SPTCP"])


    avg_delay=[np.sum(FDM_d)/np.sum(FDM_p),np.sum(multi_d)/np.sum(multi_p),np.sum(single_d)/np.sum(single_p) ]
    index=np.arange(3)
    ax4.scatter(index,avg_delay, marker="o", s=50)
    ax4.set_xlabel('Protocols')
    ax4.set_ylabel('Average Delay (Sec)')
    ax4.set_xticks(index )
    ax4.set_xticklabels(["FDM","MPTCP","SPTCP"])
    #ax4.set_yscale("log")
    ax4.set_ylim([0,6])
    fig.tight_layout()
    plt.show()
