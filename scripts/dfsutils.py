
import sys
import networkx as nx
import math
import time
import random
import multiprocessing


# Define operator partition
class OperatorPartition:
    def __init__(self, logicalOperatorId, logicalOperatorName, partition, parallelism, downNode, upNode, outboundtype, compute, state, network):
        # The logical operator id this OP belongs to
        self.logicalOperatorId = logicalOperatorId
        # The logical operator this OP belongs to
        self.logicalOperatorName = logicalOperatorName
        # Which partition within this logical operator
        self.partition = partition
        # The number of tasks this OP has
        self.parallelism = parallelism
        # List of downstream OPs
        self.downNode = downNode
        # List of upstream OPs
        self.upNode = upNode
        # Outbound link type of this op
        self.outboundtype = outboundtype
        # Resource requirement
        self.compute = compute
        self.state = state
        self.network = network


# The structure keeping track of the current placement plan
class CurPlace:
    def __init__(self, workers_num, workers_slot):
        # The remaining number of available slots
        self.leftSlots = workers_num * workers_slot
        # Key: the task placement group on a node
        # Value: the number nodes that have the same task placement group and the monotonic resource usage
        # TODO: Now only consider homogeneous node (same # of slots)
        self.map = {NodePlacement([]): NodePlacementInfo(workers_num, ResourceUsage(0, 0, 0))}


# Hashable structure that defines the task placement group on a node
# This is the key type of CurPlace.map
# Note: the key of dict is immutable, so NodePlacement will not be modified.
# NodePlacement will only be deleted and create new one upon change (see updateCurPlace() for details)
class NodePlacement:
    # list is a String[] that stores the current placed tasks on this node in sorted order
    def __init__(self, list):
        self.list = list
    def __hash__(self):
        s = ""
        for i in self.list:
            s += i
        return hash(s)
    def __eq__(self, other):
        if (self.__class__ != other.__class__):
            return False
        if (len(self.list) != len(other.list)):
            return False
        for i in range(len(self.list)):
            if (self.list[i] != other.list[i]):
                return False
        return True
    def __repr__(self):
        return f"NodePlacement({self.list})"
    

# The structure containing node info: value field of CurPlace.map
class NodePlacementInfo:
    def __init__(self, num, res):
        self.num = num
        # Accumulated resource usage
        self.res = res
    def __repr__(self):
        return f"NodePlacementInfo(num:{self.num}, res:{self.res})"
    


# Accumulated resource usage on a node
class ResourceUsage:
    def __init__(self, compute, state, network):
        self.compute = compute
        self.state = state
        self.network = network
    def __repr__(self):
        return f"(cpcost:{self.compute}, iocost:{self.state}, nwcost:{self.network})"

    def getMax(self, other):
        self.compute = max(self.compute, other.compute)
        self.state = max(self.state, other.state)
        self.network = max(self.network, other.network)

    def isDominated(self, other):
        return self.allLargerEqual(other) and self.anyLarger(other)

    def allLargerEqual(self, other):
        return self.compute >= other.compute and self.state >= other.state and self.network >= other.network

    def anyLarger(self, other):
        return self.compute > other.compute or self.state > other.state or self.network > other.network


# Node structure used by inner DFS call stack
# Each one corresponds to a physical node that has available slots to deploy tasks of current OP
class Node:
    def __init__(self, key, res, deployment):
        # NodePlacement
        self.key = key
        # ResourceUsage
        self.res = res
        # How many tasks of the current OP to be deployed
        self.deployment = deployment
    def __repr__(self):
        return f"Node({self.key, self.deployment})"
    

# Threshold parameter for dfs
class ThresholdRatio:
    def __init__(self, compute, state, network):
        self.compute = compute
        self.state = state
        self.network = network
    def printDetails(self):
        return("compute="+str(self.compute)+"    state="+str(self.state)+"    network="+str(self.network))

# Configurable parameters for tuning the threshold parameter
class MicrobenchmarkParas:
    def __init__(self, planNum, step_ratio_compute, step_ratio_io, step_ratio_network):
        self.planNum = planNum
        self.step_ratio_compute = step_ratio_compute
        self.step_ratio_io = step_ratio_io
        self.step_ratio_network = step_ratio_network


# Define exception in microbenmark
class HasAvailablePlan(Exception):
    pass


# Helper function to tolerate float number wired behaviors
def almost_equal(num1, num2, tolerance=1e-6):
    return abs(num1 - num2) <= tolerance


def checkJobGraphMicroBenchmark(JobGraph):
    # Check on graph costs
    totalCompute = 0    # must be > 0 on each op
    totalIO = 0
    totalNetwork = 0
    for node in JobGraph.nodes():
        # compute
        if JobGraph.nodes[node]['cpcost'] <= 0 or JobGraph.nodes[node]['cpcost'] != JobGraph.nodes[node]['cpcost']:
            sys.exit("cpcost invalid on node: "+str(JobGraph.nodes[node]))
        totalCompute += JobGraph.nodes[node]['cpcost']
        # IO
        if JobGraph.nodes[node]['iocost'] < 0 or JobGraph.nodes[node]['iocost'] != JobGraph.nodes[node]['iocost']:
            sys.exit("iocost invalid on node: "+str(JobGraph.nodes[node]))
        totalIO += JobGraph.nodes[node]['iocost']
        # network
        if JobGraph.nodes[node]['nwcost'] < 0 or JobGraph.nodes[node]['nwcost'] != JobGraph.nodes[node]['nwcost']:
            sys.exit("nwcost invalid on node: "+str(JobGraph.nodes[node]))
        totalNetwork += JobGraph.nodes[node]['nwcost']
    if totalNetwork == 0:
        sys.exit("All network cost are zero! not possible")
    
    return totalIO


def round_if_close(x, tolerance=1e-9):
    if math.isclose(x, round(x), abs_tol=tolerance):
        return round(x)
    else:
        return x


class TimeManager:
    def __init__(self, lowBound, highBound):
        self.lowBound = lowBound
        self.highBound = highBound
        self.nextTime = time.time()
    
    def updateNextTime(self):
        processDuration = random.uniform(self.lowBound, self.highBound)
        self.nextTime = time.time() + processDuration

    def timeOut(self):
        return time.time() >= self.nextTime

# Structure maintained in all processes
class SharedPool:
    def __init__(self, totalProcess):
        self.queue = multiprocessing.SimpleQueue()
        self.lock = multiprocessing.Lock()
        self.avaiProcess = multiprocessing.Value("i", totalProcess)
        # DEBUG
        # self.tempLock = multiprocessing.Lock()
        # self.tempNum = multiprocessing.Value("i", 0)

    def scheduleProcess(self, args):
        self.queue.put(args)

    def terminate(self):
        self.queue.put(None)
    
    def earlyExit(self):
        self.queue.put("foundPlan")

    def acquireProcess(self):
        with self.lock:
            if self.avaiProcess.value > 0:
                self.avaiProcess.value -= 1
                return True
            else:
                return False
            

# Structure maintained in the main process
class ProcessPool:
    def __init__(self, sharedPool, processInitFunc, processFunc, plans):
        self.totalProcess = sharedPool.avaiProcess.value
        self.sharedPool = sharedPool
        self.pool = multiprocessing.Pool(processes=self.totalProcess, initializer=processInitFunc, initargs=(self.sharedPool,))
        self.processFunc = processFunc
        # application specific data
        self.plans = plans

    def start(self):
        while True:
            processArgs = self.sharedPool.queue.get()
            if processArgs is None:
                break
            if processArgs == "foundPlan":
                print("[NOTE] dfs found a plan and early exit!")
                return True
            # start process
            self.pool.apply_async(self.processFunc, args=processArgs, callback=self.endProcess)

        print("Multi-process DFS finish")
        return False
        # self.pool.close()
        # self.pool.join()

    def endProcess(self, result):
        if isinstance(result, Exception):
            print("Error:", result)
            sys.exit()
        # append the results from child processes to main process
        self.plans.extend(result)
        # add the terminated process back to the process pool
        with self.sharedPool.lock:
            self.sharedPool.avaiProcess.value += 1
            if self.sharedPool.avaiProcess.value == self.totalProcess:
                self.sharedPool.terminate()


class ProcessPoolPara:
    def __init__(self, numProcess, low, high):
        self.numProcess = numProcess
        self.low = low
        self.high = high


def if2PlansValuesSame(plans1, plans2):
    ps1 = set()
    for p in plans1:
        planTaskList = []
        for key, value in p.items():
            cp = "{:.1f}".format(value.res.compute)
            st = "{:.1f}".format(value.res.state)
            nw = "{:.1f}".format(value.res.network)
            l = [cp, st, nw]
            valueStr = '-'.join(l)
            planTaskList.append(valueStr)
        planTaskList.sort()
        ps1.add('+'.join(planTaskList))
    
    ps2 = set()
    for p in plans2:
        planTaskList = []
        for key, value in p.items():
            cp = "{:.1f}".format(value.res.compute)
            st = "{:.1f}".format(value.res.state)
            nw = "{:.1f}".format(value.res.network)
            l = [cp, st, nw]
            valueStr = '-'.join(l)
            planTaskList.append(valueStr)
        planTaskList.sort()
        ps2.add('+'.join(planTaskList))

    return ps1 == ps2

def if2PlansSame(plans1, plans2):
    ps1 = set()
    for p in plans1:
        planTaskList = []
        for key, value in p.items():
            keyStr = ''.join(key.list)
            planTaskList.append(keyStr)
        planTaskList.sort()
        ps1.add(''.join(planTaskList))

    ps2 = set()
    for p in plans2:
        planTaskList = []
        for key, value in p.items():
            keyStr = ''.join(key.list)
            planTaskList.append(keyStr)
        planTaskList.sort()
        ps2.add(''.join(planTaskList))

    return ps1 == ps2