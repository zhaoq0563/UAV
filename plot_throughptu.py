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
sp_x, sp_sat, sp_wlan=([]for i in range(3))
line=f.readline()
while line:
    l=line.split(",")
    for k in range(len(l)):
        l[k]=l[k].strip("\n")
        l[k]=l[k].strip("\"")
    x,sat,wlan=l
    sp_x.append(float(x))
    sp_wlan.append(float(wlan)/10**6)
    sp_sat.append(float(sat)/10**6)
    line=f.readline()
f.close()
fig, axes = plt.subplots(nrows=2,ncols=1, figsize=(20,4))
ax1=axes[0]
ax2=axes[1]
ax1.plot(fdm_x,fdm_wlan,color='#FE0000',linestyle=':',marker='x',markersize=3,label='mptcp_wlan')
ax1.plot(fdm_x,fdm_sat,color='#27BAFF',linestyle=':',marker='o',markersize=3,label='mptcp_sat')
ax1.plot(fdm_x,fdm_tot,color='#FFD800',linestyle='--',linewidth=3,label='mptcp_total')
ax2.plot(sp_x,sp_wlan,color='#FE0000',linestyle=':',marker='x',markersize=3,label='sptcp_wlan')
ax2.plot(sp_x,sp_sat,color='#27BAFF',linestyle=':',marker='o',markersize=3,label='sptcp_sat')
ax1.set_xlim(0, 180)
ax1.set_ylim(0, 2)
ax2.set_xlim(0, 180)
ax2.set_ylim(0, 2)
ax1.legend(loc='best')
ax2.legend(loc='best')
plt.show()
