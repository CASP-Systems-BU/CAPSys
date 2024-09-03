import dfs as singleDFS
import dfsMultiProcess as multiDFS
import pickle
from dfsutils import *

if __name__ == "__main__":

    workers_ip=['192.168.1.8', '192.168.1.9', '192.168.1.12', '192.168.1.13']
    workers_num = len(workers_ip)
    workers_slot = 8

    ratio = ThresholdRatio(1.5, 1.5, 0.6)
    graphFile = "/home/tidb/Desktop/data/deem.pkl"
    jobGraph = pickle.load(open(graphFile, "rb"))

#     ######################### Single process DFS #########################
#     print("\nSingle-process dfs")
#     singleDFSproc = singleDFS.DFSprocess(workers_num, workers_slot, ratio, jobGraph, "compute", findBound=False)
#     optimals, plansSinle=singleDFSproc.process()

    ######################### Multi process DFS #########################
    print("\nMulti-process dfs")
    numProcess = 16
    timePeriodLow = 0.5
    timePeriodHigh = 0.6

    processPoolPara = ProcessPoolPara(numProcess, timePeriodLow, timePeriodHigh)
    dfsproc=multiDFS.DFSprocess(workers_num, workers_slot, ratio, jobGraph, "compute", processPoolPara, findBound=False)
    optimals, plansMulti=dfsproc.process()

    # Test results
    # print("Compare if 2 plans are the same:",if2PlansSame(plansSinle, plansMulti) and if2PlansValuesSame(plansSinle, plansMulti))


    ####################### Example for early exit #######################
    # This is an exmple how to early exit dfs when the 1st plan is found (same as single process dfs)
    print()
    dfsproc=multiDFS.DFSprocess(workers_num, workers_slot, ratio, jobGraph, "compute", processPoolPara, findBound=True)
    try:
        optimals, plans=dfsproc.process()
    except HasAvailablePlan as e:
        print(e)
