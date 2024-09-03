import sys, os

# python3 runall_multi.py expjson/multi.json multi

fjson=sys.argv[1]
RUNID=sys.argv[2]

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


changeConfigFileOnScheduling("custom")
RUNID_custom = RUNID + "_custom"
for rx in range(10,12):
    os.system("python3 runds2placementmulti.py "+fjson+" start "+RUNID_custom+str(rx)+" -1 custom")

changeConfigFileOnScheduling("even")
RUNID_custom = RUNID + "_even"
for rx in range(1,10):
    os.system("python3 runds2placementmulti.py "+fjson+" start "+RUNID_custom+str(rx)+" -1 even")

changeConfigFileOnScheduling("random")
RUNID_random = RUNID + "_random"
for rx in range(10):
    os.system("python3 runds2placementmulti.py "+fjson+" start "+RUNID_random+str(rx)+" -1 random")
