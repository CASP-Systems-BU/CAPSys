import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os,sys
from datetime import datetime
import matplotlib.ticker as mticker
import pytz

# Usage:
#     python3 plottimeline.py q5_2122_12000/exp_r5_schedulercfg_0 "Source"
#     python3 plottimeline.py q5_2122_12000/exp_r5_schedulercfg_0 "192.168.1.13"

colorlist=['r','g','b','c','m','y']
pp=sys.argv[1]
op=sys.argv[2]
print(pp)


fnames=os.listdir(pp)
print(fnames)
fl=[]
fk=[]
for fn in fnames:
    if(fn.endswith('.log')):
        fl.append(fn)
    if(op in fn):
        fk.append(fn)
print("------------------------------------------------------------")
latencyvalist=[]
taskkwlist={'numRecordsInPerSecond':[], 'numRecordsOutPerSecond':[], 'busyTimeMsPerSecond':[], 'backPressuredTimeMsPerSecond':[],
        'Shuffle.Netty.Input.Buffers.inputQueueLength': [], 'Shuffle.Netty.Input.Buffers.inPoolUsage': [],
        'Shuffle.Netty.Output.Buffers.outputQueueLength': [], 'Shuffle.Netty.Output.Buffers.outPoolUsage': [],
        '.rocksdb_bytes_read': [], '.rocksdb_bytes_written': [],
        }
tmgrkwlist={'Status.JVM.CPU.Load':[], 'Status.JVM.Threads.Count':[],
        }
if(op.startswith('192')):
    kwlist=tmgrkwlist        # taskmanager metrics
else:
    kwlist=taskkwlist        # subtask metrics

minlt=9999999999999
maxlt=0


FNTSIZE=48
FIGX=30
FIGY=20
FIGD=80
FIGLINE=3
fig,axl = plt.subplots(len(kwlist)+1, 1, sharey=False, sharex=True, figsize=(FIGX, FIGY), dpi=FIGD)


# read flink metrics
for fn in fk:
    ff=open(pp+'/'+fn, 'r').readlines()
    fcnt=0
    for _ll, _lc in enumerate(ff):
        lt=_lc.split('; ')[0]
        for lc in _lc.split('; '):
            for kw in kwlist.keys():
                if(kw in lc):
                    ldict=eval(lc.replace('[','').replace(']',''))
                    kwlist[kw].append((int(lt), float(ldict['value'])))
                    minlt=min(int(lt), minlt)
                    maxlt=max(int(lt), maxlt)
                    fcnt+=1
    print(pp+'/'+fn,fcnt)


# read latency
for fn in fl:
    ff=open(pp+'/'+fn, 'r').readlines()
    fcnt=0
    _starttimestamp=ff[0].split(',')[0]
    starttimestamp=datetime.strptime(_starttimestamp, '%Y-%m-%d %H:%M:%S')
    for _ll, _lc in enumerate(ff):
        if(('%latency%' in _lc)and(not 'latencyFromOperator' in _lc)):
            _ltimestamp=_lc.split(',')[0]
            ltimestamp=datetime.strptime(_ltimestamp, '%Y-%m-%d %H:%M:%S')
            duration=(ltimestamp-starttimestamp).total_seconds()
            if(duration>=600):                            # ignore first 10min
                ll=_lc.split('%latency%')[1].split('%')[0]
                lt=_lc.split('%latency%')[1].split('%')[1]
                latencyvalist.append((int(lt), int(ll)))
                minlt=min(int(lt), minlt)
                maxlt=max(int(lt), maxlt)
                fcnt+=1
    print(pp+'/'+fn,fcnt)

print("------------------------------------------------------------")

# plot flink metrics
for kidx, kw in enumerate(kwlist.keys()):
    valist=kwlist[kw]
    valist.sort()
    nvalist=np.array(valist)
    #print(kw, valist)
    if(len(nvalist)>0):
        print(kw,'    avg:',np.average(nvalist[:,1]),'    min:',np.min(nvalist[:,1]),'    max:',np.max(nvalist[:,1]),'    p50:',np.percentile(nvalist[:,1], 50))
        axl[kidx].plot(nvalist[:,0], nvalist[:,1], marker='.', color=colorlist[kidx % len(colorlist)], label=kw)
    axl[kidx].set_title(kw)
    #axl[kidx].set_xlabel("timestamp")
    axl[kidx].set_xlim([minlt, maxlt])
    axl[kidx].ticklabel_format(style='plain')
    axl[kidx].xaxis.set_major_locator(mticker.MultipleLocator(100000))
    plt.setp(axl[kidx].get_xticklabels(), rotation=90)


# plot latency
latencyvalist.sort()
nvalist=np.array(latencyvalist)
#print("latency", latencyvalist)
print("latency_avg", np.average(nvalist[:,1]))
print('latency_p99', np.percentile(nvalist[:,1], 99))
axl[-1].plot(nvalist[:,0], nvalist[:,1], marker='.', color=colorlist[-1], label='latency')
axl[-1].set_title("latency")
axl[-1].set_xlabel("timestamp")
axl[-1].set_xlim([minlt, maxlt])
axl[-1].ticklabel_format(style='plain')
axl[-1].xaxis.set_major_locator(mticker.MultipleLocator(100000))
plt.setp(axl[-1].get_xticklabels(), rotation=90)

date_minlt=datetime.utcfromtimestamp(minlt/1000).replace(tzinfo=pytz.UTC).astimezone(pytz.timezone('US/Eastern'))
date_maxlt=datetime.utcfromtimestamp(maxlt/1000).replace(tzinfo=pytz.UTC).astimezone(pytz.timezone('US/Eastern'))
date_range="timestamp range:"+str(date_minlt)[:20]+'--'+str(date_maxlt)[:20]
print(date_range)
text_kwargs = dict(ha='center', va='center', fontsize=28, color='C1')
plt.suptitle(pp+" "+op+" "+date_range)
plt.legend()
plt.show()
