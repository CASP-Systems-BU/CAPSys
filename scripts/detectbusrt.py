import os,sys
import matplotlib.pyplot as plt

########################## Inputs
# log file
# fn = "/Users/geoffrey/Desktop/deem_a/exp_r5_schedulercfg_1001/Inference_0"
# fn = "/Users/geoffrey/Desktop/deem_a/exp_r5_schedulercfg_1002/Inference_1"
#fn = "/Users/geoffrey/Desktop/deem_a/exp_r5_schedulercfg_1003/Inference_0"
fn = "/home/tidb/Desktop/data/flink-placement-16/expresult/deem_a/exp_r5_schedulercfg_1003/Inference_0"
# sliding window size (second)
window_size = 20
# X times standard deviation
Xsdev = 1.5

lines=open(fn, 'r').readlines()

metric = 'busyTimeMsPerSecond'
times_temp = []
values = []

for _ll, _lc in enumerate(lines):
    time = _lc.split('; ')[0]
    for lc in _lc.split('; '):
        if(metric in lc):
            ldict=eval(lc.replace('[','').replace(']',''))
            times_temp.append(int(time))
            values.append(float(ldict['value']))

if (len(times_temp) == 0):
    sys.exit("0 elements in timeline")
start = times_temp[0]
times = []
for t in times_temp:
    times.append((t-start)/1000)

# Now use 2 pointers to get sliding windows
windows = []
windowTimes = []
windowValues = []
for l in range(len(times)):
    r = l
    totalValue = values[l]
    ct = 1
    while (r+1<len(times) and times[r+1] - times[l] <= window_size):
        r += 1
        totalValue += values[r]
        ct += 1
    if (r+1 == len(times)):
        break
    windows.append((times[l], times[r]))
    windowTimes.append((times[l]+times[r])/2)
    windowValues.append(totalValue/ct)
# for i in range(len(windows)):
#     print(windows[i],windowValues[i])

# Calculate threshold
windowsMean = sum(windowValues)/len(windowValues)
variance = sum([((x - windowsMean) ** 2) for x in windowValues]) / len(windowValues)
windowsSdev = variance ** 0.5
threshold = windowsMean + Xsdev * windowsSdev
# print("mean:",windowsMean)
# print("standard deviation:",windowsSdev)
print("threshold:",threshold)

# Get spikes
spikes = []
# spikeMaxs = []
# spikeMeans = []

inSpike = False
spikeStart = 0
spikeEnd = 0
for i in range(len(windows)):
    if (windowValues[i] >= threshold):
        if (inSpike):
            spikeEnd = windowTimes[i]
        else:
            inSpike = True
            spikeStart = windowTimes[i]
    else:
        if (inSpike):  # now end the spike
            inSpike = False
            spikes.append((spikeStart, spikeEnd))
# for i in range(len(spikes)):
#     print(spikes[i])
print("Monitored time range:",times[-1]-times[0],"seconds")
print("Num of spikes:",len(spikes))

# Figure
fig, ax = plt.subplots(figsize=(12, 3),tight_layout=True)
ax.plot(times, values, label='Time points')
ax.plot(windowTimes, windowValues, color='red', label='Moing average')
ax.set_ylabel('Busy rate (ms)', fontsize=13)
ax.set_xlabel('Timeline (seconds)', fontsize=13)
ax.legend(fontsize=13)
plt.show()






# Parameters: TBD


# Now implement the algo.


# read all data points first

# set up w: window size of the moving average (ME)
# 

# data point every 5 seconds.




