import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os,sys
from datetime import datetime
import matplotlib.ticker as mticker
import pytz
import json
import pickle

def custom_formatter(x):
    return f"{x:.2f}"

np.set_printoptions(threshold=np.inf, linewidth=np.inf, edgeitems=10)
np.set_printoptions(formatter={'all': custom_formatter})

# Usage:
#     python3 plotdynamictimeline.py deem_dynamicjson_custom expjson/deem_dynamic.json

colorlist=['r','g','b','c','m','y']
path=sys.argv[1]
#fjson=sys.argv[2]
#cfg=json.loads(open(fjson,'r').read())
#srcratelist=cfg['srcratelist']    # target_input_rate
#jarargs=cfg['jarargs']

loglist=[x for x in os.listdir(path) if os.path.isdir(os.path.join(path, x))]
jglist=[x for x in os.listdir(path) if x.endswith('jg.pkl')]
print(path)
print(loglist)
print(jglist)
DEPLOYTIME=int(open(path+'/DEPLOYTIME', 'r').read())
print('DEPLOYTIME', DEPLOYTIME)
print("------------------------------------------------------------")

def getDurationTops():
    srcparallelism=int(jarargs["psrc"])
    duration=0
    rl=srcratelist[0]["Source"].split("_")
    for i in range(0,len(rl),2):
        _rate = int(rl[i])
        _dur  = int(rl[i+1])
        duration += _dur
    return(duration)

def getCurrentTops(tt):
    srcparallelism=int(jarargs["psrc"])
    duration=int(tt)-DEPLOYTIME
    rl=srcratelist[0]["Source"].split("_")
    for i in range(0,len(rl),2):
        _rate = int(rl[i])
        _dur  = int(rl[i+1])
        duration -= _dur
        if(duration<=0):
            return(_rate*srcparallelism)
    return(-1)    # job already finished

def getoprid(name):
    if("Source" in name):
        return(0)
    elif("Transform" in name):
        return(1)
    elif("Compress" in name):
        return(2)
    elif("Inference" in name):
        return(3)
    elif("Sink" in name):
        return(4)

FNTSIZE=48
FIGX=30
FIGY=20
FIGD=80
FIGLINE=3
fig,axl = plt.subplots(7, 1, sharey=False, sharex=True, figsize=(FIGX, FIGY), dpi=FIGD)


# timelist=[]
# target_input_rate=[]
# for i in range(getDurationTops()):
#     timelist.append(i+DEPLOYTIME)
#     target_input_rate.append(getCurrentTops(i+DEPLOYTIME))
# axl[0].plot(timelist, target_input_rate, marker=',', color='b', label='target_input_rate')


for itrid in loglist:
    print('################################################ iteration '+itrid)
    jgFiles=[itrid+'_jg.pkl', itrid+'_warmup_jg.pkl']
    cpuFiles=[itrid+'_cpuutil.pkl', itrid+'_warmup_cpuutil.pkl']
    for _f in range(2):
        jgFile=path+'/'+jgFiles[_f]
        cpuFile=path+'/'+cpuFiles[_f]
        if(os.path.exists(jgFile)):
            jg=pickle.load(open(jgFile, 'rb'))
            cpu=pickle.load(open(cpuFile, 'rb'))
            total_task=0
            total_optimaltask=0
            for opr in jg.nodes():
                total_task += jg.nodes()[opr]['parallelism']
                total_optimaltask += jg.nodes()[opr]['optimalparallelism']
                oprid=getoprid(jg.nodes()[opr]['name'])
                axl[oprid].set_title(jg.nodes()[opr]['name'])
                timelist=[int(x) for x in jg.nodes()[opr]['_timestamp']]
                print('------------------')
                print('_timestamp', timelist)
                if("Source" in jg.nodes()[opr]['name']):
                    ax2 = axl[oprid].twinx()
                    ax2.set_ylim(0, 1000)
                    axl[oprid].plot(timelist, jg.nodes()[opr]['_oop'], marker='.', color='g', label='oop')
                    axl[oprid].plot(timelist, jg.nodes()[opr]['_tops'], marker='.', color='r', label='target_input_rate')
                    ax2.plot(timelist, jg.nodes()[opr]['_bkpstime'], marker='.', color='y', label='bkpstime')
                    print(jg.nodes()[opr]['name'])
                    print('_oop', jg.nodes()[opr]['_oop'])
                    print('_bkpstime', jg.nodes()[opr]['_bkpstime'])
                else:
                    print(jg.nodes()[opr]['name'])
                    print('parallelism', jg.nodes()[opr]['parallelism'])
                    print('optimalparallelism', jg.nodes()[opr]['optimalparallelism'])
                    print('_optimalparallelism', jg.nodes()[opr]['_optimalparallelism'])
                    print('_busytime', jg.nodes()[opr]['_busytime'])
                    ax2 = axl[oprid].twinx()
                    ax2.set_ylim(0, 1000)
                    axl[oprid].set_yticks(np.arange(0, 20, 1))
                    axl[oprid].plot(timelist, [jg.nodes()[opr]['parallelism'] for x in timelist], marker=',', color='r', label='parallelism', alpha=0.6)
                    axl[oprid].text(timelist[0], jg.nodes()[opr]['parallelism'], str(jg.nodes()[opr]['parallelism']), fontsize=12, color='r')
                    if(len(timelist)==len(jg.nodes()[opr]['_optimalparallelism'])):    # warmup does not have _optimalparallelism
                        axl[oprid].plot(timelist, jg.nodes()[opr]['_optimalparallelism'] , marker=',', color='b', label='optimalparallelism', alpha=0.6)
                        axl[oprid].plot(timelist, [jg.nodes()[opr]['optimalparallelism'] for x in timelist], marker=',', color='g', label='optimalparallelism', alpha=0.6)
                    ax2.plot(timelist, jg.nodes()[opr]['_busytime'] , marker=',', color='y', label='busytime')
                if(itrid=="1"):
                    axl[oprid].legend(loc='lower right')
                    ax2.legend(loc='upper right')
                print('------------------')

            print("numTasks: ",total_task)
            print("numTasksForNextIteration: ",total_optimaltask)
            print("numTaskManager: ",len(cpu))
            axl[5].plot(timelist, [len(cpu) for x in timelist], marker=',', color='r', label='numTaskManager')
            axl[5].text(timelist[0], len(cpu), str(len(cpu)), fontsize=12, color='r' )
            axl[5].set_ylim(0, 6)
            axl[6].plot(timelist, [total_task for x in timelist], marker=',', color='r', label='numTasks')
            axl[6].text(timelist[0], total_task, str(total_task), fontsize=12, color='r')
            axl[6].plot(timelist, [total_optimaltask for x in timelist], marker=',', color='g', label='numTasksForNextIteration')
            axl[6].text(timelist[0], total_optimaltask, str(total_optimaltask), fontsize=12, color='g')
            axl[6].set_ylim(0, 6*8)
            if(itrid=="1"):
                axl[5].legend(loc='upper right')
                axl[6].legend(loc='upper right')

# plt.setp(axl[1].get_xticklabels(), rotation=90)
plt.ticklabel_format(style='plain')
axl[-1].get_xaxis().get_major_formatter().set_scientific(False)

plt.suptitle(path)
# plt.show()
plt.savefig(path.replace('.','').replace('/','')+'.pdf')
