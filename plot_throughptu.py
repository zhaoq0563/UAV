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
    fdm_wlan.append(float(wlan))
    fdm_sat.append(float(sat))
    fdm_tot.append(float(tot))
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
    sp_wlan.append(float(wlan))
    sp_sat.append(float(sat))
    line=f.readline()
f.close()
color_sequence = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
                  '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
                  '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
                  '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5']
fig, axes = plt.subplots(nrows=1,ncols=1, figsize=(20,3))
axes.plot(fdm_x,fdm_wlan,color=color_sequence[0],linestyle=':',label='fdm_wlan')
axes.plot(fdm_x,fdm_sat,color=color_sequence[1],linestyle=':',)
axes.plot(fdm_x,fdm_tot,color=color_sequence[2],linestyle='--',)
axes.plot(sp_x,sp_wlan,color=color_sequence[3],linestyle='--',)
axes.plot(sp_x,sp_sat,color=color_sequence[4],linestyle='--')
axes.set_xlim(0, 200)
axes.set_ylim(0, 2000000)
axes.legend()
plt.show()
