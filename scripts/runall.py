import sys, os
from exputils import *

fjson=sys.argv[1]
RUNID=sys.argv[2]

# 0: start from the profiling phase
# 1 or any other input: start from the 2nd iteration (profiling folder already exists)
START_ITER=sys.argv[3]


def changeConfigFileOnScheduling(policy):
    file = open('aws/flink-conf.yaml', 'r')
    lines = file.readlines()
    file.close()

    file = open('aws/flink-conf.yaml', 'w')

    if policy == "custom":
        for line in lines:
            if "jobmanager.scheduler: Custom" in line:
                file.write("jobmanager.scheduler: Custom\n")
            elif "cluster.evenly-spread-out-slots: true" in line:
                file.write("#cluster.evenly-spread-out-slots: true\n")
            else:
                file.write(line)
    elif policy == "even":
        for line in lines:
            if "jobmanager.scheduler: Custom" in line:
                file.write("#jobmanager.scheduler: Custom\n")
            elif "cluster.evenly-spread-out-slots: true" in line:
                file.write("cluster.evenly-spread-out-slots: true\n")
            else:
                file.write(line)
    elif policy == "random":
        for line in lines:
            if "jobmanager.scheduler: Custom" in line:
                file.write("#jobmanager.scheduler: Custom\n")
            elif "cluster.evenly-spread-out-slots: true" in line:
                file.write("#cluster.evenly-spread-out-slots: true\n")
            else:
                file.write(line)
    else:
        file.close()
        sys.exit("policy input error")
    file.close()

if START_ITER == '0':
    changeConfigFileOnScheduling("custom")
    os.system("python3 runds2placement.py "+fjson+" start profile 0 custom")
else:
    
    changeConfigFileOnScheduling("custom")
    RUNID_custom = RUNID + "_custom"
    for rx in range(7):
        os.system("python3 runds2placement.py "+fjson+" start "+RUNID_custom+str(rx)+" "+START_ITER + " custom")

    changeConfigFileOnScheduling("even")
    RUNID_even = RUNID + "_even"
    for rx in range(7):
        os.system("python3 runds2placement.py "+fjson+" start "+RUNID_even+str(rx)+" "+START_ITER + " even")

    changeConfigFileOnScheduling("random")
    RUNID_random = RUNID + "_random"
    for rx in range(7):
        os.system("python3 runds2placement.py "+fjson+" start "+RUNID_random+str(rx)+" "+START_ITER + " random")
