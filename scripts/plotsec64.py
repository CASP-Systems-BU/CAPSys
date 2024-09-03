from re import sub
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os,sys
from datetime import datetime
import matplotlib.ticker as mticker
import pytz
import json
import pickle
import matplotlib

def custom_formatter(x):
    return f"{x:.2f}"

np.set_printoptions(threshold=np.inf, linewidth=np.inf, edgeitems=10)
np.set_printoptions(formatter={'all': custom_formatter})

# Usage:
#     python3 plotsec64.py deem_dynamicjson_custom/ deem_dynamicjson_even/ deem_dynamicjson_random/

colorr=['darkred', 'red', 'orange']
colorg=['forestgreen', 'limegreen', 'lime']
colorb=['darkblue', 'blue', 'skyblue']

pathlist=[sys.argv[1], sys.argv[2], sys.argv[3]]
XLIMSEC=int(sys.argv[4])
# fjson=sys.argv[4]
# cfg=json.loads(open(fjson,'r').read())
# srcratelist=cfg['srcratelist']    # target_input_rate
# jarargs=cfg['jarargs']

FNTSIZE=48
FIGX=25
FIGY=20
FIGD=50
FIGLINE=9
fig,axl = plt.subplots(3, 1, sharey=False, sharex=True, figsize=(FIGX, FIGY), dpi=FIGD)
matplotlib.rcParams['font.size'] = FNTSIZE


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

def removeGap(sorted_combined_list, interval):
    # Initialize new x and y lists
    new_x = []
    new_y = []
    gaps=[]

    # Counter for continuous x-axis values
    x_counter = 0

    offset=0
    for i in range(len(sorted_combined_list)):
        x=sorted_combined_list[i][0]
        y=sorted_combined_list[i][1]
        tmp=x-sorted_combined_list[i-1][0]
        if(i>0 and tmp>2*interval):
            offset=x-new_x[i-1]-2*interval
            gaps.append(x-offset)
        new_x.append(x-offset)
        new_y.append(y)
        x_counter += 1  # Increment the counter for the next x-axis value

    return(new_x, new_y, gaps)


savefname=""
for _i, path in enumerate(pathlist):
    subtitle=path.replace('.','').replace('/','')
    savefname=savefname+subtitle+"_"
    if('custom' in subtitle):
        subtitle="CAPSys"
    elif('even' in subtitle):
        subtitle='Evenly'
    elif('random' in subtitle):
        subtitle='Default'
    axl[_i].set_title(subtitle, fontsize=FNTSIZE)
    loglist=[x for x in os.listdir(path) if os.path.isdir(os.path.join(path, x))]
    jglist=[x for x in os.listdir(path) if x.endswith('jg.pkl')]
    print(path)
    print(loglist)
    print(jglist)
    DEPLOYTIME=int(open(path+'/DEPLOYTIME', 'r').read())
    print('DEPLOYTIME', DEPLOYTIME)
    print("------------------------------------------------------------")

    # timelist=[]
    # target_input_rate=[]
    # for i in range(getDurationTops()):
    #     timelist.append(i+DEPLOYTIME)
    #     target_input_rate.append(getCurrentTops(i+DEPLOYTIME))
    # # axl[0].plot(timelist, target_input_rate, marker=',', color='b', label='target_input_rate')

    # list of tuples(x,y)
    loop=[]
    ltops=[]
    lbkpstime=[]
    ltotalTM=[]
    ltotalTask=[]

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
                    #axl[0][_i].set_title(subtitle)
                    timelist=[int(x)-DEPLOYTIME for x in jg.nodes()[opr]['_timestamp']]
                    print('------------------')
                    print('_timestamp', timelist)
                    if("Source" in jg.nodes()[opr]['name']):
                        loop = loop + list(zip(timelist, jg.nodes()[opr]['_oop']))
                        ltops = ltops + list(zip(timelist, jg.nodes()[opr]['_tops']))
                        lbkpstime = lbkpstime + list(zip(timelist, jg.nodes()[opr]['_bkpstime']))
                        print(jg.nodes()[opr]['name'])
                        print('_oop', jg.nodes()[opr]['_oop'])
                        print('_tops', jg.nodes()[opr]['_tops'])
                        print('_bkpstime', jg.nodes()[opr]['_bkpstime'])
                    print('------------------')

                print("numTasks: ",total_task)
                print("numTasksForNextIteration: ",total_optimaltask)
                print("numTaskManager: ",len(cpu))
                ltotalTM = ltotalTM + list(zip(timelist, [len(cpu) for x in timelist]))
                ltotalTask = ltotalTask + list(zip(timelist, [total_task for x in timelist]))

    loop=sorted(loop, key=lambda xy: xy[0])
    oop_x, oop_y, gaps = removeGap(loop, 5)

    ltops=sorted(ltops, key=lambda xy: xy[0])
    tops_x, tops_y, gaps = removeGap(ltops, 5)

    lbkpstime=sorted(lbkpstime, key=lambda xy: xy[0])
    bkpstime_x, bkpstime_y, gaps = removeGap(lbkpstime, 5)

    ltotalTM=sorted(ltotalTM, key=lambda xy: xy[0])
    totalTM_x, totalTM_y, gaps = removeGap(ltotalTM, 5)

    ltotalTask=sorted(ltotalTask, key=lambda xy: xy[0])
    totalTask_x, totalTask_y, gaps = removeGap(ltotalTask, 5)

    for _xg, xg in enumerate(gaps):
        axl[_i].axvline(x=xg, color='dimgrey', linestyle='--', linewidth = 4)
        axl[_i].text(xg-100, 10, str(_xg+1), color='black', fontsize=FNTSIZE/3*2, bbox=dict(facecolor='white', alpha=0.5))
    axl[_i].plot(oop_x, oop_y, linestyle='-', linewidth=4, color=colorr[1], label='throughput ')
    axl[_i].plot(tops_x, tops_y, linestyle='-', linewidth=4, color=colorg[0], label='target input rate ')

    # axl[_i].plot(bkpstime_x, bkpstime_y, marker=',', color=colorr[_i], label='bkpstime ')

    # axl[_i].plot(totalTM_x, totalTM_y, marker=',', color=colorr[_i], label='numTaskManager ')
    # axl[_i].text(totalTM_x[0], totalTM_y[0], str(totalTM_y[0]), fontsize=FNTSIZE, color=colorr[_i])
    # axl[_i].set_ylim(0, 6)

    axl2=axl[_i].twinx()
    axl2.plot(totalTask_x, totalTask_y, color=colorb[1], linestyle='-', linewidth=4, label='# tasks ')
    #axl2.text(totalTask_x[i], totalTask_y[i], str(totalTask_y[i]), fontsize=FNTSIZE, color=colorb[1])
    print("totalTask_", totalTask_x, totalTask_y)
    #axl[_i].twinx().set_ylim(0, 6*8)
    axl2.set_yticks(np.arange(0, 6*8, 8))

    axl[_i].get_xaxis().get_major_formatter().set_scientific(False)
    axl[_i].set_ylabel('Rate (rec/s)', fontsize=FNTSIZE)
    axl2.set_ylabel('# Tasks', fontsize=FNTSIZE)
    axl[_i].tick_params(axis='x', labelsize=FNTSIZE)  # Set font size for x-axis
    axl[_i].tick_params(axis='y', labelsize=FNTSIZE)  # Set font size for y-axis
    axl[_i].set_xlim(0, XLIMSEC)

    # axl[_i].legend()
    # axl2.legend()

# merge legends of axl and axl2 to the same box
new_labels, new_handles = [], []
handles, labels = axl[0].get_legend_handles_labels()
for handle, label in zip(handles, labels):
    new_labels.append(label)
    new_handles.append(handle)
handles, labels = axl2.get_legend_handles_labels()
for handle, label in zip(handles, labels):
    new_labels.append(label)
    new_handles.append(handle)
print(new_labels, new_handles)
axl[0].legend(new_handles, new_labels, loc='lower right', fontsize=FNTSIZE, ncol=3, bbox_to_anchor=(1.0, 1.1))


# plt.setp(axl[1].get_xticklabels(), rotation=90)
plt.ticklabel_format(style='plain')
axl[-1].set_xlabel('Elapsed Time(sec)', fontsize=FNTSIZE)

plt.tight_layout()
#plt.show()
plt.savefig(savefname+'.pdf')
