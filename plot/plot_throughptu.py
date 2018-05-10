#!/usr/bin/python
import matplotlib.pyplot as plt
import numpy as np
from numpy import array

f=open("affact-fdm.txt",'r')
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
f=open("affact-mptcp.txt",'r')
f.readline()
sp_x, sp_wlan, sp_sat, sp_tot=([]for i in range(4))
line=f.readline()
while line:
    l=line.split(",")
    for k in range(len(l)):
        l[k]=l[k].strip("\n")
        l[k]=l[k].strip("\"")
    x,wlan,sat,tot=l
    sp_x.append(float(x))
    sp_wlan.append(float(wlan)/10**6)
    sp_sat.append(float(sat)/10**6)
    sp_tot.append(float(tot)/10**6)
    line=f.readline()
f.close()
fig, axes = plt.subplots(nrows=2,ncols=1, figsize=(8,8))
ax1=axes[0]
ax2=axes[1]
ax2.plot(fdm_x,fdm_wlan,color='#FE0000',linestyle='-',linewidth=3, marker='x',markersize=5,label='User1-WiFi')
ax2.plot(fdm_x,fdm_sat,color='#27BAFF',linestyle='-',linewidth=3, marker='o',markersize=5,label='User1-LTE')
ax2.plot(fdm_x,fdm_tot,color='#FFD800',linestyle='-',linewidth=3, marker='^',markersize=5,label='User3-WiFi')
#ax1.plot(fdm_x,fdm_tot,color='#FFD800',linestyle='--',linewidth=3,label='FDM_total')
ax1.plot(sp_x,sp_wlan,color='#FE0000',linestyle='-',linewidth=3, marker='x',markersize=5,label='User1-WiFi')
ax1.plot(sp_x,sp_sat,color='#27BAFF',linestyle='-',linewidth=3, marker='o',markersize=5,label='User1-LTE')
ax1.plot(sp_x,sp_tot,color='#FFD800',linestyle='-',linewidth=3, marker='^',markersize=5,label='User3-WiFi')
ax1.set_xlim(-2, 40)
ax1.set_ylim(0, 5)
ax2.set_xlim(-2, 40)
ax2.set_ylim(0, 5)
ax1.legend(loc='best')
ax2.legend(loc='best')
fig.text(0.5, 0.04, 'Time (s)', ha='center', va='center')
fig.text(0.06, 0.5, 'Throughput (Mbps)', ha='center', va='center', rotation='vertical')
ax1.set_title('MPTCP')
ax2.set_title('MPTCP+FDM')
plt.show()
