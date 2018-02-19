for i in range(0,len(senderList)):
           throughtput, delay,byte=(0.0,0.0,0)
           for j in range(host_eth[senderList[i]]):
               f_name="host"+str(senderList[i])+"eth"+str(j)+".stat"
               duration=0
               f=open(f_name,'r')
               for line in f:
                   if line.startswith('|'):
                       l=line.strip().strip('|').split()
                       if 'Duration:' in l:
                           duration=float(l[1])
                       if '<>' in l:
                           byte+=float(l[4])
                           throughtput+=float(l[4])*8/duration
                           delay+=byte*float(l[6])
               f.close()
           delay/=byte
           out_file="host"+str(senderList[i])+"-wireshark.stat"
           o=open(out_file,'w')
           o.write("Throughput: "+str(throughtput)+"\nDelay: "+str(delay))
           o.close()