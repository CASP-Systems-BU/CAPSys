import matplotlib.pyplot as plt
import sys, os, time, json, requests, json, math, time, pickle
import networkx as nx
import numpy as np
import pandas as pd
from collections import defaultdict
from datetime import datetime
import textwrap

def wrap_text(text, max_length):
    """Wrap text based on a specified maximum line length."""
    return textwrap.fill(text, max_length)

kwdlist=['parallelism', 'busytime', 'bkpstime', 'tip', 'oip', 'tips', 'top', 'oop', 'tops', 'optimalparallelism']

def getFlinkLogLatency(fpath, skipsec):
    # read latency
    latencyvalist=[]
    minlt=9999999999999
    maxlt=0
    ff=open(fpath, 'r').readlines()
    fcnt=0
    _starttimestamp=ff[0].split(',')[0]
    starttimestamp=datetime.strptime(_starttimestamp, '%Y-%m-%d %H:%M:%S')
    for _ll, _lc in enumerate(ff):
        if(('%latency%' in _lc)and(not 'latencyFromOperator' in _lc)):
            _ltimestamp=_lc.split(',')[0]
            ltimestamp=datetime.strptime(_ltimestamp, '%Y-%m-%d %H:%M:%S')
            duration=(ltimestamp-starttimestamp).total_seconds()
            if(duration>=skipsec):                            # ignore first several sec
                ll=_lc.split('%latency%')[1].split('%')[0]
                lt=_lc.split('%latency%')[1].split('%')[1]
                latencyvalist.append((int(lt), int(ll)))
                minlt=min(int(lt), minlt)
                maxlt=max(int(lt), maxlt)
                fcnt+=1
    print(fpath,fcnt, len(latencyvalist))
    return(latencyvalist)
#     if(len(latencyvalist)>0):
#         latencyvalist.sort()
#         nvalist=np.array(latencyvalist)
#         # print("  latency_avg", np.average(nvalist[:,1]))
#         # print('  latency_p99', np.percentile(nvalist[:,1], 99))
#         return(( np.average(nvalist[:,1]) , np.percentile(nvalist[:,1], 99) ))
#     return((-1, -1))    # this log file does not contain latency counter

def getFlinkLogPlacement(fpath):
    res=[]
    kwd='switched from INITIALIZING to RUNNING'
    ff=open(fpath, 'r').readlines()
    for _ll, _lc in enumerate(ff):
        if(kwd in _lc):
            opr=_lc.split("[] - ")[1].replace(kwd, "").replace("\n", "")
            res.append(opr)
    return(res)


def getOneRun(jpath, skipsec):
    jg=pickle.load(open(jpath+'/jg.pkl', 'rb'))
    vlist=jg.nodes()
    dat={}

    for vid in vlist:
        vname=jg.nodes()[vid]['name']
        dat[vname]={}
        print("===================",vname)
        for kw in kwdlist:
            print(kw, jg.nodes()[vid][kw])
            dat[vname][kw]=jg.nodes()[vid][kw]

    ff=["flink-ubuntu-taskexecutor-0-ip-192-168-1-101.log", "flink-ubuntu-taskexecutor-0-ip-192-168-1-102.log", "flink-ubuntu-taskexecutor-0-ip-192-168-1-103.log", "flink-ubuntu-taskexecutor-0-ip-192-168-1-104.log"]
    latencyvalist=[]
    for _f in ff:
        print("===================")
        platency = getFlinkLogLatency(jpath+'/'+_f, 30+skipsec)
        latencyvalist = latencyvalist + platency
        ppl=getFlinkLogPlacement(jpath+'/'+_f)
        for opr in ppl:
            print("        ", opr)

    if(len(latencyvalist)>0):
        latencyvalist.sort()
        nvalist=np.array(latencyvalist)
    pavg=np.average(nvalist[:,1])
    pp99=np.percentile(nvalist[:,1], 99)
    print("  latency_avg: ", pavg)
    print("  latency_p99: ", pp99)
    dat['_job_latency']={}
    dat['_job_latency']['avg']=pavg
    dat['_job_latency']['p99']=pp99

    print("===================")
    return(dat)


def getOneRunMetric(dat, opr, key):
    return(dat[opr][key])

def getOneRunOpr(dat):
    res=list(dat.keys())
    res.remove("_job_latency")
    return(res)


def getMultipleRun(fpath, iterno='iter1'):
    pathlist=[]
    datlist=defaultdict(lambda: defaultdict(list))
    subfolders = [d for d in os.listdir(fpath) if os.path.isdir(os.path.join(fpath, d))]
    print(subfolders)
    for sf in subfolders:
        if(sf.endswith(iterno)):
            jpath=os.path.join(fpath,sf)
            dat=getOneRun(jpath, 360)
            oprlist=getOneRunOpr(dat)
            pathlist.append(sf)
            datlist['_job_latency']['avg'].append(getOneRunMetric(dat, '_job_latency', 'avg'))
            datlist['_job_latency']['p99'].append(getOneRunMetric(dat, '_job_latency', 'p99'))
            for opr in oprlist:
                for kwd in kwdlist:
                    datlist[opr][kwd].append(getOneRunMetric(dat, opr, kwd))
    return(datlist, pathlist)




# cmd=sys.argv[1]
# jpath=sys.argv[2]
# if(cmd=="one"):
#     skipsec=int(sys.argv[3])
#     getOneRun(jpath, skipsec)
# elif(cmd=="multi"):
#     iterno=sys.argv[3]
#     datlist, pathlist=getMultipleRun(jpath, iterno)
#     print(datlist, pathlist)
#     fig, axs = plt.subplots(len(datlist.keys()), len(kwdlist), figsize=(15, 5))
#     for ki, kx in enumerate(datlist.keys()):
#         axs[ki][0].set_ylabel(wrap_text(kx, 10))
#         for kj, ky in enumerate(datlist[kx].keys()):
#             axs[ki][kj].boxplot(datlist[kx][ky])
#             axs[ki][kj].set_title(ky)
#     plt.subplots_adjust(wspace=0.7, hspace=0.7, left=0.1, right=0.95, bottom=0.05, top=0.95)  # Adjust as needed
#     plt.tight_layout()
#     plt.show()

getOneRun(sys.argv[1], 120)
