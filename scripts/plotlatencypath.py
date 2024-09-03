import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os,sys
from datetime import datetime


# Usage: python3 plotlatencypath.py ../expresult/new/exp_r5_schedulercfg_1001_200ms_awsa/ 600

skipsec=int(sys.argv[2])
colorlist=['r','g','b','c','m','y']
pp=sys.argv[1]
print(pp)

fnames=os.listdir(pp)
fl=[]
for fn in fnames:
    if(fn.endswith('.log')):
        fl.append(fn)
print("------------------------------------------------------------")
tracklist=dict()
latencylist=dict()

for fn in fl:
    ff=open(pp+'/'+fn, 'r').readlines()
    snkcnt=0
    oprcnt=0
    _starttimestamp=ff[0].split(',')[0]
    starttimestamp=datetime.strptime(_starttimestamp, '%Y-%m-%d %H:%M:%S')
    for _ll, _lc in enumerate(ff):
        if('%latency%' in _lc):
            _ltimestamp=_lc.split(',')[0]
            ltimestamp=datetime.strptime(_ltimestamp, '%Y-%m-%d %H:%M:%S')
            duration=(ltimestamp-starttimestamp).total_seconds()
            if(duration>=skipsec):                            # ignore first 10min
                lc=_lc.split('%latency%')[1].split('%')
                latency=int(lc[0])
                markedTime=int(lc[2])
                sourceSubTaskID=lc[5]
                currentSubTaskID=lc[6]
                currentTaskManagerID=lc[7]
                oprType=lc[8]
                vval=(latency, currentSubTaskID, currentTaskManagerID)
                if(not(sourceSubTaskID in tracklist)):
                    tracklist[sourceSubTaskID]=dict()
                if(not(markedTime in tracklist[sourceSubTaskID])):
                    tracklist[sourceSubTaskID][markedTime]=[]
                tracklist[sourceSubTaskID][markedTime].append(vval)
                tracklist[sourceSubTaskID][markedTime].sort()
                if('latencyFromSink' in oprType):
                    snkcnt+=1
                if('latencyFromOperator' in oprType):
                    oprcnt+=1
    print(pp+'/'+fn, snkcnt, oprcnt)

print(tracklist.keys())    # id of all source subtask

for ksrc in tracklist.keys():
    latencylist[ksrc]=dict()
    for kmrk in tracklist[ksrc].keys():
        try:
            latencylist[ksrc][kmrk]=max([x[0] for x in tracklist[ksrc][kmrk]])
        except:
            latencylist[ksrc][kmrk]=-1    # invalid record

for ksrc in tracklist.keys():
    myKeys=list(latencylist[ksrc].keys())
    myKeys=sorted(myKeys, key=lambda x: latencylist[ksrc][x])
    tracklist[ksrc] = {i: tracklist[ksrc][i] for i in myKeys}
    for kmrk in tracklist[ksrc].keys():
        print(ksrc, kmrk, tracklist[ksrc][kmrk], latencylist[ksrc][kmrk])
