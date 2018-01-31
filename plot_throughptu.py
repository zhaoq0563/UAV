#!/usr/bin/python
import matplotlib.pyplot as plt
import numpy as np
from numpy import array

f=open("mptcp_fdm.txt",'r')
f.readline()
fdm_x, fdm_wlan, fdm_sat, fdm_tot=([]for i in range(4))
line=f.readline()
while line:
    l=line.split(",")
    for k in range(len(l)):
        l[k]=l[k].strip("\n")
        l[k]=l[k].strip("\"")
    x,wlan,sat,tot=l
    fdm_x.append(float(x))
    fdm_wlan.append(float(wlan)/10**6)
    fdm_sat.append(float(sat)/10**6)
    fdm_tot.append(float(tot)/10**6)
    line=f.readline()
f.close()
f=open("sptcp.txt",'r')
f.readline()
sp_x, sp_wlan, sp_sat=([]for i in range(3))
line=f.readline()
while line:
    l=line.split(",")
    for k in range(len(l)):
        l[k]=l[k].strip("\n")
        l[k]=l[k].strip("\"")
    x,wlan,sat=l
    sp_x.append(float(x))
    sp_wlan.append(float(wlan)/10**6)
    sp_sat.append(float(sat)/10**6)
    line=f.readline()
f.close()
color_sequence = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
                  '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
                  '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
                  '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5']
fig, axes = plt.subplots(nrows=2,ncols=1, figsize=(20,4))
ax1=axes[0]
ax2=axes[1]
ax1.plot(fdm_x,fdm_wlan,color=color_sequence[0],linestyle=':',marker='x',markersize=3,label='fdm_wlan')
ax1.plot(fdm_x,fdm_sat,color=color_sequence[2],linestyle=':',marker='x',markersize=3,label='fdm_sat')
ax1.plot(fdm_x,fdm_tot,color='black',linestyle='--',linewidth=1,label='fdm_tot')
ax2.plot(sp_x,sp_wlan,color=color_sequence[0],linestyle=':',marker='x',markersize=3,label='sp_wlan')
ax2.plot(sp_x,sp_sat,color=color_sequence[2],linestyle=':',marker='x',markersize=3,label='sp_sat')
ax1.set_xlim(0, 180)
ax1.set_ylim(0, 2)
ax2.set_xlim(0, 180)
ax2.set_ylim(0, 2)
ax1.legend(loc='best')
ax2.legend(loc='best')
plt.show()
