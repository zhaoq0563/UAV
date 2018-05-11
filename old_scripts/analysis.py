#!/usr/bin/python

import os, sys, datetime

def findnSeek(flag, line, findStr, result, str_split):
    if flag==1 and line.find(findStr)!=-1:
        result = result+line.split('=')[1].strip().split(' ')[0]
        result = result+str_split
        return(result)
    else:
        result = result + ''
        return(result)


def extractStat(sndList, recvList, folderName):
    # decode of sender files
    for i in range(0, len(sndList)):
        initialFileName = '/home/osboxes/D-ITG-2.8.1-r1023/bin/log/sta'+str(sndList[i])+'.log'
        decodedSenderFile = folderName+'/sta'+str(sndList[i])+'.txt'
        os.system('/home/osboxes/D-ITG-2.8.1-r1023/bin/ITGDec '+str(initialFileName)+' > '+str(decodedSenderFile))

    # decode of receiver files
    for i in range(0, len(sndList)):
        initialFileName = '/home/osboxes/D-ITG-2.8.1-r1023/bin/log/sta'+str(sndList[i])+'-h'+str(recvList[0])+'.log'
        decodedRecvFile = folderName+'/sta'+str(sndList[i])+'-h'+str(recvList[0])+'.txt'
        os.system('/home/osboxes/D-ITG-2.8.1-r1023/bin/ITGDec '+str(initialFileName)+' > '+str(decodedRecvFile))


def statAnalysis(sndList, recvList, folderName):
    time = datetime.datetime.now()
    fileName = 'result_'+str(time)+'.csv'
    results = open(folderName+'/'+fileName, 'w')
    str_ini = 'station,'

    # sender host list
    for i in range(0, len(sndList)):
        str_ini = str_ini+'sta'+str(sndList[i])
        if i<len(sndList)-1:
            str_ini = str_ini+','
        else:
            str_ini = str_ini+'\n'

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
        decodedRecvFile = folderName+'/sta'+str(sndList[i])+'-h'+str(recvList[0])+'.txt'
        flag = 0
        f = open(decodedRecvFile, 'r')
        if i<len(sndList)-1:
            str_split = ','
        else:
            str_split = '\n'

        # read separate files
        while 1:
            line = f.readline()

            if not line:
                f.close()
                break
            if line.find('TOTAL RESULTS')!=-1:
                flag = 1

            total_time = findnSeek(flag, line, 'Total time', total_time, str_split)
            total_packets = findnSeek(flag, line,'Total packets', total_packets, str_split)
            min_delay = findnSeek(flag, line, 'Minimum delay', min_delay, str_split)
            max_delay = findnSeek(flag, line, 'Maximum delay', max_delay, str_split)
            avg_delay = findnSeek(flag, line, 'Average delay', avg_delay, str_split)
            avg_jitter = findnSeek(flag, line, 'Average jitter', avg_jitter, str_split)
            sd_delay = findnSeek(flag, line, 'Delay standard', sd_delay, str_split)
            avg_bit_rate = findnSeek(flag, line, 'Average bitrate', avg_bit_rate, str_split)
            avg_pkt_rate = findnSeek(flag, line, 'Average packet', avg_pkt_rate, str_split)

    # write results to files
    results.write(str_ini)
    results.write(total_time)
    results.write(total_packets)
    results.write(min_delay)
    results.write(max_delay)
    results.write(avg_delay)
    results.write(avg_jitter)
    results.write(sd_delay)
    results.write(avg_bit_rate)
    results.write(avg_pkt_rate)
    results.close()


if __name__ == '__main__':
    sndList = eval(sys.argv[1])
    recvList = [1]
    folderName = sys.argv[2]

    extractStat(sndList, recvList, folderName)
    statAnalysis(sndList, recvList, folderName)