import sys, os

fjson=sys.argv[1]
RUNID=sys.argv[2]

# python3 rundynamicall.py expjson/deem_unlimit_dynamic.json 700x8

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
RUNID_custom = "custom_"+RUNID
os.system("python3 rundynamic.py "+fjson+" start "+RUNID_custom)

changeConfigFileOnScheduling("even")
RUNID_even = "even_"+RUNID
os.system("python3 rundynamic.py "+fjson+" start "+RUNID_even)

changeConfigFileOnScheduling("random")
RUNID_random = "random_"+RUNID
os.system("python3 rundynamic.py "+fjson+" start "+RUNID_random)
