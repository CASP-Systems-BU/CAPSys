import pickle

graphFile = "/Users/geoffrey/Desktop/jg.pkl"
jobGraph = pickle.load(open(graphFile, "rb"))

parallelism = {}
# source ds2 para: 2
parallelism["Source__Source___TimestampAssigner"] = 2
# transform ds2 para: 1
parallelism["Transform"] = 5
# window ds2 para: 10
parallelism["Window_SlidingEventTimeWindows_3600000__60000___EventTimeTrigger__CountBids__WindowResultFunciton_"] = 8
# sink ds2 para: 1
parallelism["Sink"] = 1

# for node, attrs in jobGraph.nodes(data=True):
#     print(attrs['name'])

for node in jobGraph.nodes:
    jobGraph.nodes[node]['cpcost'] = (jobGraph.nodes[node]['tips']/parallelism[jobGraph.nodes[node]["name"]])*jobGraph.nodes[node]['_cpcost']
    jobGraph.nodes[node]['iocost'] = (jobGraph.nodes[node]['tips']/parallelism[jobGraph.nodes[node]["name"]])*jobGraph.nodes[node]['_iocost']/1024/1024
    if (jobGraph.nodes[node]['tips'] == 0): # If the node is a source node
        jobGraph.nodes[node]['cpcost']=(jobGraph.nodes[node]['tops']/parallelism[jobGraph.nodes[node]["name"]])*jobGraph.nodes[node]['_cpcost']
        jobGraph.nodes[node]['iocost']=(jobGraph.nodes[node]['tops']/parallelism[jobGraph.nodes[node]["name"]])*jobGraph.nodes[node]['_iocost']/1024/1024
    jobGraph.nodes[node]['nwcost'] = (jobGraph.nodes[node]['tops']/parallelism[jobGraph.nodes[node]["name"]])*jobGraph.nodes[node]['_nwcost']/1024/1024
    # Change parallelism
    jobGraph.nodes[node]['optimalparallelism'] = parallelism[jobGraph.nodes[node]["name"]]

pickle.dump(jobGraph, open("/Users/geoffrey/Desktop/updatedjg.pkl", "wb"))

