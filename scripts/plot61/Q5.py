import pickle
import sys
import matplotlib.pyplot as plt
from exputils import *
import os
import numpy as np
import matplotlib.ticker as mticker
import os
import statistics


skipsec=90

logs=["flink-ubuntu-taskexecutor-0-ip-192-168-1-101.log", "flink-ubuntu-taskexecutor-0-ip-192-168-1-102.log", "flink-ubuntu-taskexecutor-0-ip-192-168-1-103.log", "flink-ubuntu-taskexecutor-0-ip-192-168-1-104.log"]

customFolder = "../q5/q5_custom"
evenFolder = "../q5/q5_even"
randomFolder = "../q5/q5_random"

nodeList = ["192.168.1.8", "192.168.1.9", "192.168.1.12", "192.168.1.13"]
customCPUsum = []
evenCPUsum = []
randomCPUsum = []
customCPUsdv = []
evenCPUsdv = []
randomCPUsdv = []

targetTput = 0

# HPS
customSourceBkp = []
customTput = []
customP99 = []
customAveLatency = []

with os.scandir(customFolder) as entries:
    # traverse all trails
    for entry in entries:
        if entry.name[0] == '.':
            continue
        
        # # read cpu metrics
        # cpu = pickle.load(open(customFolder+"/"+entry.name+"/cpuutil.pkl", 'rb'))
        # cpuByNode = []
        # for ip in nodeList:
        #     cpulist = cpu[ip]
        #     cpuByNode.append(sum(cpulist)/len(cpulist))
        # customCPUsum.append(sum(cpuByNode)/1000)
        # customCPUsdv.append(statistics.stdev(cpuByNode))

        jg=pickle.load(open(customFolder+"/"+entry.name+"/jg.pkl", 'rb'))
        for node, attrs in jg.nodes(data=True):
            if 'Source' in attrs['pname']:
                customSourceBkp.append(attrs['bkpstime'])
                customTput.append(attrs['oop'])
                targetTput = attrs['tops']
        latencyvalist=[]
        for log in logs:
            platency = getFlinkLogLatency(customFolder+'/'+entry.name+'/'+log, 30+skipsec)
            latencyvalist = latencyvalist + platency
        if(len(latencyvalist)>0):
            latencyvalist.sort()
            nvalist=np.array(latencyvalist)
        pavg=np.average(nvalist[:,1])
        pp99=np.percentile(nvalist[:,1], 99)
        customP99.append(pp99)
        customAveLatency.append(pavg)


# Even
evenSourceBkp = []
evenTput = []
evenP99 = []
evenAveLatency = []
with os.scandir(evenFolder) as entries:
    # traverse all trails
    for entry in entries:
        if entry.name[0] == '.':
            continue

        # # read cpu metrics
        # cpu = pickle.load(open(evenFolder+"/"+entry.name+"/cpuutil.pkl", 'rb'))
        # cpuByNode = []
        # for ip in nodeList:
        #     cpulist = cpu[ip]
        #     cpuByNode.append(sum(cpulist)/len(cpulist))
        # evenCPUsum.append(sum(cpuByNode)/1000)
        # evenCPUsdv.append(statistics.stdev(cpuByNode))

        jg=pickle.load(open(evenFolder+"/"+entry.name+"/jg.pkl", 'rb'))
        for node, attrs in jg.nodes(data=True):
            if 'Source' in attrs['pname']:
                evenSourceBkp.append(attrs['bkpstime'])
                evenTput.append(attrs['oop'])
        latencyvalist=[]
        for log in logs:
            platency = getFlinkLogLatency(evenFolder+'/'+entry.name+'/'+log, 30+skipsec)
            latencyvalist = latencyvalist + platency
        if(len(latencyvalist)>0):
            latencyvalist.sort()
            nvalist=np.array(latencyvalist)
        pavg=np.average(nvalist[:,1])
        pp99=np.percentile(nvalist[:,1], 99)
        evenP99.append(pp99)
        evenAveLatency.append(pavg)


# Random
randomSourceBkp = []
randomTput = []
randomP99 = []
randomAveLatency = []

with os.scandir(randomFolder) as entries:
    # traverse all trails
    for entry in entries:
        if entry.name[0] == '.':
            continue

        # # read cpu metrics
        # cpu = pickle.load(open(randomFolder+"/"+entry.name+"/cpuutil.pkl", 'rb'))
        # cpuByNode = []
        # for ip in nodeList:
        #     cpulist = cpu[ip]
        #     cpuByNode.append(sum(cpulist)/len(cpulist))
        # randomCPUsum.append(sum(cpuByNode)/1000)
        # randomCPUsdv.append(statistics.stdev(cpuByNode))

        jg=pickle.load(open(randomFolder+"/"+entry.name+"/jg.pkl", 'rb'))
        for node, attrs in jg.nodes(data=True):
            if 'Source' in attrs['pname']:
                randomSourceBkp.append(attrs['bkpstime'])
                randomTput.append(attrs['oop'])
        latencyvalist=[]
        for log in logs:
            platency = getFlinkLogLatency(randomFolder+'/'+entry.name+'/'+log, 30+skipsec)
            latencyvalist = latencyvalist + platency
        if(len(latencyvalist)>0):
            latencyvalist.sort()
            nvalist=np.array(latencyvalist)
        pavg=np.average(nvalist[:,1])
        pp99=np.percentile(nvalist[:,1], 99)

        randomP99.append(pp99)
        randomAveLatency.append(pavg)


# ================================== figure

def format_func(value, tick_number):
    # Divide by 1000 and format as '1k', '2k', etc.
    return f'{int(value / 1000)}k' if value >= 1000 else int(value)

def format_decimal(value, tick_number):
    # Format with no leading zero for decimal numbers
    return f'{value:.2f}'.lstrip('0') if value != 0 else '0'


c1 = (255, 208, 111)
c2 = (255, 230, 183)
# c2 = (239, 138, 71)
c3 = (170, 220, 224)
c4 = (82, 143, 173)

c5 = (231, 98, 84)
c_light = (255, 230, 183)

c1 = tuple([x/255.0 for x in c1])
c2 = tuple([x/255.0 for x in c2])
c3 = tuple([x/255.0 for x in c3])
c4 = tuple([x/255.0 for x in c4])
c5 = tuple([x/255.0 for x in c4])
c_light = tuple([x/255.0 for x in c_light])

border_color = 'black'
border_width = 1.1
bar_width = 0.5


xLabel = ['CAPS', 'Even', 'Dft']
colors = [c1, c3, c4]

fig, ax = plt.subplots(3,1, figsize=(1.4, 4.0))

tickSize = 7
bottomTickSize = 7
labelSize = 8

# (1) ==============================================================

boxplot1 = ax[0].boxplot([customTput, evenTput, randomTput], widths=bar_width, patch_artist=True,
                        medianprops=dict(color='red'), flierprops=dict(marker='o', color='black', markersize=2))
for patch, color in zip(boxplot1['boxes'], colors):
    patch.set_facecolor(color)

ax[0].yaxis.set_major_formatter(format_func)
ax[0].set_ylabel('rec/s', fontsize=labelSize)
ax[0].set_xticklabels(xLabel, fontsize=bottomTickSize)
ax[0].tick_params(axis='y', labelsize=tickSize)
# ax[0].set_ylim([10800, targetTput+280])
ax[0].yaxis.set_major_formatter(format_func)
targetTput = 118600
ax[0].axhline(y=targetTput, color='green', linestyle='--')
# ax[0].set_xlabel("(a) Throughput", fontsize=labelSize)

# (2) ==============================================================

for i in range(len(customSourceBkp)):
    customSourceBkp[i] /= 10
for i in range(len(evenSourceBkp)):
    evenSourceBkp[i] /= 10
for i in range(len(randomSourceBkp)):
    randomSourceBkp[i] /= 10

boxplot0 = ax[1].boxplot([customSourceBkp, evenSourceBkp, randomSourceBkp], widths=bar_width, patch_artist=True,
                        medianprops=dict(color='red'), flierprops=dict(marker='o', color='black', markersize=2))
for patch, color in zip(boxplot0['boxes'], colors):
    patch.set_facecolor(color)

ax[1].set_ylabel('%', fontsize=labelSize)
ax[1].tick_params(axis='y', labelsize=tickSize)
ax[1].set_xticklabels(xLabel, fontsize=bottomTickSize)
# ax[2].tick_params(axis='x', labelsize=9)
# ax[1].yaxis.set_major_formatter(format_decimal)
ax[1].set_ylim([-3, 103])
# ax[1].set_xlabel("(b) Backpressure", fontsize=labelSize)


meanTputCAPS = sum(customTput)/len(customTput)
meanTputEven = sum(evenTput)/len(evenTput)
meanTputDefault = sum(randomTput)/len(randomTput)

minTputCAPS = boxplot1['whiskers'][0*2].get_ydata()[1]
minTputEven = boxplot1['whiskers'][1*2].get_ydata()[1]
minTputDefault = boxplot1['whiskers'][2*2].get_ydata()[1]

maxTputCAPS = boxplot1['whiskers'][0*2 + 1].get_ydata()[1] 
maxTputEven = boxplot1['whiskers'][1*2 + 1].get_ydata()[1] 
maxTputDefault = boxplot1['whiskers'][2*2 + 1].get_ydata()[1] 

print("Tput")
print(f"    CAPS: [{minTputCAPS}, {maxTputCAPS}], {meanTputCAPS}")
print(f"    Even: [{minTputEven}, {maxTputEven}], {meanTputEven}")
print(f"    Default: [{minTputDefault}, {maxTputDefault}], {meanTputDefault}")

meanBCAPS = sum(customSourceBkp)/len(customSourceBkp)
meanBEven = sum(evenSourceBkp)/len(evenSourceBkp)
meanBDefault = sum(randomSourceBkp)/len(randomSourceBkp)

minBCAPS = boxplot0['whiskers'][0*2].get_ydata()[1]
minBEven = boxplot0['whiskers'][1*2].get_ydata()[1]
minBDefault = boxplot0['whiskers'][2*2].get_ydata()[1]

maxBCAPS = whisker_high = boxplot0['whiskers'][0*2 + 1].get_ydata()[1] 
maxBEven = whisker_high = boxplot0['whiskers'][1*2 + 1].get_ydata()[1] 
maxBDefault = whisker_high = boxplot0['whiskers'][2*2 + 1].get_ydata()[1] 

print("B-pressure")
print(f"    CAPS: [{minBCAPS}, {maxBCAPS}], {meanBCAPS}")
print(f"    Even: [{minBEven}, {maxBEven}], {meanBEven}")
print(f"    Default: [{minBDefault}, {maxBDefault}], {meanBDefault}")


# (3) ==============================================================

for i in range(len(customAveLatency)):
    customAveLatency[i] /= 1000
for i in range(len(evenAveLatency)):
    evenAveLatency[i] /= 1000
for i in range(len(randomAveLatency)):
    randomAveLatency[i] /= 1000

boxplot3 = ax[2].boxplot([customAveLatency, evenAveLatency, randomAveLatency], widths=bar_width, patch_artist=True,
                         medianprops=dict(color='red'), flierprops=dict(marker='o', color='black', markersize=2))
for patch, color in zip(boxplot3['boxes'], colors):
    patch.set_facecolor(color)
ax[2].set_ylabel('seconds', fontsize=labelSize)
ax[2].tick_params(axis='y', labelsize=tickSize)
ax[2].set_xticklabels(xLabel, fontsize=bottomTickSize)
ax[2].set_ylim([0.0, 1.5])
# ax[3].set_ylim([0.3, 2.45])
# ax[2].set_xlabel("(c) Average Latency", fontsize=labelSize)

meanAveLatencyCAPS = sum(customAveLatency)/len(customAveLatency)
meanAveLatencyEven = sum(evenAveLatency)/len(evenAveLatency)
meanAveLatencyDefault = sum(randomAveLatency)/len(randomAveLatency)

minAveLatencyCAPS = boxplot3['whiskers'][0*2].get_ydata()[1]
minAveLatencyEven = boxplot3['whiskers'][1*2].get_ydata()[1]
minAveLatencyDefault = boxplot3['whiskers'][2*2].get_ydata()[1]

maxAveLatencyCAPS = boxplot3['whiskers'][0*2 + 1].get_ydata()[1] 
maxAveLatencyEven = boxplot3['whiskers'][1*2 + 1].get_ydata()[1] 
maxAveLatencyDefault = boxplot3['whiskers'][2*2 + 1].get_ydata()[1] 

print("Average Latency")
print(f"    CAPS: [{minAveLatencyCAPS}, {maxAveLatencyCAPS}], {meanAveLatencyCAPS}")
print(f"    Even: [{minAveLatencyEven}, {maxAveLatencyEven}], {meanAveLatencyEven}")
print(f"    Default: [{minAveLatencyDefault}, {maxAveLatencyDefault}], {meanAveLatencyDefault}")


plt.tight_layout()
plt.subplots_adjust(top=0.96, bottom=0.1, left=0.35, right=0.98)
plt.subplots_adjust(wspace=0.55)
#plt.show()

print("targetTput:", targetTput)
plt.savefig('./q5-aggregate.png', dpi=300)
plt.close()
