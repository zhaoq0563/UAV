#!/usr/bin/python

import os
from numpy import array
import numpy as np
import matplotlib.pyplot as plt


if __name__ == '__main__':
    fdm_throughput=1.9323
    sp_throughput= 1.42
    fdm_delay=0.1994
    sp_delay= 0.4423
    req=3

    n_groups = 1

    fig, axes = plt.subplots(nrows=1,ncols=2, figsize=(10,4))
    ax=axes[0]
    ax2=axes[1]
    index = np.arange(n_groups)*2
    bar_width = 0.15

    opacity = 0.4
    error_config = {'ecolor': '0.3'}

    rects1 = ax.bar(0.3, fdm_throughput, bar_width,
                    alpha=opacity, color='b',edgecolor="none",
                    label='FDM')

    rects3 = ax.bar(0.3, req-fdm_throughput, bar_width,bottom=fdm_throughput,
                    alpha=opacity, color='w', hatch='//', edgecolor="none", linewidth=0,
                    )

    rects2 = ax.bar(0.3 +0.3, sp_throughput, bar_width,
                    alpha=opacity, color='r',edgecolor="none",
                    label='MPTCP')
    rects3 = ax.bar(0.3+0.3, req-sp_throughput, bar_width,bottom=sp_throughput,
                    alpha=opacity, color='w', hatch='//', edgecolor="none", linewidth=0,
                    )

    #ax.set_xlabel('Hosts')
    ax.set_ylabel('Throughputput(Mbps)')
    #ax.set_title('Goodput performance')
    ax.set_xticks( [0.3+0.15/2, 0.3+0.15/2+0.3])
    ax.set_xticklabels(['FDM',"SPTCP"])
    #ax.legend(loc='best',fontsize=12)
    ax.set_ylim([0,5])

    rects1 = ax2.bar(0.3, fdm_delay, bar_width,
                    alpha=opacity, color='b',edgecolor="none",
                    label='FDM')
    rects2 = ax2.bar(0.3 + 0.3, sp_delay, bar_width,
                    alpha=opacity, color='r',edgecolor="none",
                    label='MPTCP')

    #ax2.set_xlabel('Hosts')
    ax2.set_ylabel('Packet delay(Sec)')
    #ax2.set_title('Delay performance')
    ax2.set_xticks([0.3+0.15/2, 0.3+0.15/2+0.3])
    ax2.set_xticklabels(['FDM',"SPTCP"])
    #ax2.legend(loc='best',fontsize=12)

    fig.tight_layout()
    plt.show()
