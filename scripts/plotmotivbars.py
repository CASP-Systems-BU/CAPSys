import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os,sys
from datetime import datetime
import matplotlib.ticker as mticker

pd.set_option('display.max_rows', None)


def plotdf(expdf):
    FNTSIZE=48
    FIGX=30
    FIGY=20
    FIGD=96
    FIGLINE=3
    fig,axl = plt.subplots(figsize=(FIGX, FIGY), dpi=FIGD)
    width_1 = 0.3

    axl.bar(np.arange(len(expdf['latency_p99'])), expdf['latency_p99'], width=width_1, tick_label=expdf.index, label = "latency_p99", color='g')
    axl.bar(np.arange(len(expdf['latency_avg']))+width_1, expdf['latency_avg'], width=width_1, tick_label=expdf.index, label="latency_avg", color='b')
    axl.set_ylabel('latency')
    axl.legend()
    plt.setp(axl.get_xticklabels(), rotation=90)

    axr=axl.twinx()
    axr.set_ylabel('Throughput')
    axr.bar(np.arange(len(expdf['numRecordsOutPerSecond_avg']))+2*width_1, expdf['numRecordsOutPerSecond_avg'], width=width_1, tick_label=expdf.index, label="Throughput", color='r')
    axr.legend()
    plt.show()



# Usage: python3 plotposterbars.py ../expresult/motiv/q5m_a/ "Source:_Source_->_TimestampAssigner_0"

tpath=sys.argv[1]
op=sys.argv[2]

runspath = []
for x in os.listdir(tpath):
    if(x.startswith('run')):
        runspath.append(x)
print(runspath)
expid=set()
for _runs in runspath:
    ts=tpath+'/'+_runs
    for sp in os.listdir(ts):
        if('exp_' in sp):
            expid.add(sp)
expid=list(expid)
print(expid)
lexpid=len(expid)

_expdf = {'name': expid, 'true_input_rate':[0 for x in range(lexpid)],
        'latency_avg':[0 for x in range(lexpid)], 'latency_var':[0 for x in range(lexpid)], 'latency_max':[0 for x in range(lexpid)], 'latency_p99':[0 for x in range(lexpid)],
        'numRecordsInPerSecond_avg':[0 for x in range(lexpid)], 'numRecordsOutPerSecond_avg':[0 for x in range(lexpid)], 
        'busyTimeMsPerSecond_avg':[0 for x in range(lexpid)], 'backPressuredTimeMsPerSecond_avg':[0 for x in range(lexpid)],
        }
allexpdf=pd.DataFrame(_expdf).fillna(0).set_index('name')



for cnt, _expid in enumerate(expid):
    explist=[]
    for _runs in runspath:
        ts=tpath+'/'+_runs
        
        pp=ts+'/'+_expid
        fnames=os.listdir(pp)
        fl=[]
        fk=[]
        for fn in fnames:
            if(fn.endswith('.log')):
                fl.append(fn)
            if(op in fn):
                fk.append(fn)
        print("------------------------------------------------------------")
        print(pp)
        valist=[]
        kwlist={'numRecordsInPerSecond':[], 'numRecordsOutPerSecond':[], 'busyTimeMsPerSecond':[], 'backPressuredTimeMsPerSecond':[]}
        for fn in fl:
            ff=open(pp+'/'+fn, 'r').readlines()
            _starttimestamp=ff[0].split(',')[0]
            starttimestamp=datetime.strptime(_starttimestamp, '%Y-%m-%d %H:%M:%S')
            fcnt=0
            for _ll, _lc in enumerate(ff):
                if(('%latency%' in _lc)and(not 'latencyFromOperator' in _lc)):
                    _ltimestamp=_lc.split(',')[0]
                    ltimestamp=datetime.strptime(_ltimestamp, '%Y-%m-%d %H:%M:%S')
                    duration=(ltimestamp-starttimestamp).total_seconds()
                    if(duration>=10*60):                            # ignore first 10min
                        ll=_lc.split('%latency%')[1].split('%')[0]
                        valist.append(int(ll))
                        fcnt+=1
            print(pp+'/'+fn,fcnt,starttimestamp)
        for fn in fk:
            ff=open(pp+'/'+fn, 'r').readlines()
            fcnt=0
            for _ll, _lc in enumerate(ff):
                for lc in _lc.split('; '):
                    for kw in kwlist.keys():
                        if(kw in lc):
                            ldict=eval(lc.replace('[','').replace(']',''))
                            kwlist[kw].append(float(ldict['value']))
                            fcnt+=1
            print(pp+'/'+fn,fcnt)
        nvalist=np.array(valist)
        exp=dict()
        exp['name']=_expid
        exp['val']=dict()
        exp['val']['latency_avg']=np.average(nvalist)
        exp['val']['latency_var']=np.var(nvalist)
        exp['val']['latency_max']=np.max(nvalist)
        exp['val']['latency_p99']=np.percentile(nvalist, 99)
        for kw in kwlist.keys():
            exp['val'][kw+'_avg']=np.average(np.array(kwlist[kw]))
            #print(kw,np.array(kwlist[kw]))
        explist.append(exp)
        print(exp)
        for _label in exp['val'].keys():
            print(_label, exp['val'][_label])
            allexpdf.loc[_expid, _label]+=(exp['val'][_label]/len(runspath))
        


allexpdf['true_input_rate']=allexpdf['numRecordsInPerSecond_avg']/(allexpdf['busyTimeMsPerSecond_avg']/1000)
allexpdf=allexpdf.sort_values(by = ['numRecordsOutPerSecond_avg', 'latency_p99', 'latency_avg'], ascending = [True, True, True])
print(allexpdf)
