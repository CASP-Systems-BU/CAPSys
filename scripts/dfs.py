import random
import copy
import time
import pickle
import math
from dfsutils import *


class DFSprocess:

    # Check Plan cost correctness
    TESTCOST = False

    def __init__(self, workers_num, workers_slot, ratio, JobGraph, outer_dfs_order, findBound=False):
        # Trace tree node
        self.Outer_tree_node = 0
        self.Inner_tree_node = 0

        # If this run is to find bound
        self.findBound = findBound

        # Threshold
        self.threshold_compute = sys.maxsize
        self.threshold_state = sys.maxsize
        self.threshold_network = sys.maxsize

        # Outer dfs traversal order
        # "default", "compute", "state", "network"
        if not (outer_dfs_order == "default" or outer_dfs_order == "compute" or outer_dfs_order == "state" or outer_dfs_order == "network"):
            sys.exit("outer_dfs_order has to be 1 of 4 accepted types")
        self.outer_dfs_order = outer_dfs_order

        # Converted structure from JobGraph
        self.numtasks = {}

        # Hash set recording the deployed OPs
        self.deployedOps = set()

        self.workers_num=workers_num    # the number of nodes
        self.workers_slot=workers_slot    # slot number per node
        self.threshold_ratio = ratio
        self.JobGraph=JobGraph
        # check is the ratio input is valid
        if not (ratio.compute>=1):
            sys.exit("compute ratio should >= 1")
        if not (ratio.state>=1):
            sys.exit("state ratio should >= 1")
        if not (ratio.network <= 1 and ratio.network > 0):
            sys.exit("network ratio should be in (0, 1])")

    ############################# Helper Procedule call #############################

    # Given the physical execution graph, construct the operator partition list (call stack) for outer DFS
    def initStack(self):
        ops = []
        # TODO: split operator into partitions based on workload (data skew etc.). Now assuming homogeneous tasks for each operator

        # default order
        for key, operator in self.numtasks.items():
            op = OperatorPartition(key, operator['name'], 0, operator['parallelism'], operator['downNode'], operator['upNode'], operator['outboundtype'], operator['compute'], operator['state'], operator['network'])
            ops.append(op)

        # re-order the outer dfs tree to enable early prunning
        if self.outer_dfs_order == "compute":
            ops.sort(key=lambda op : op.compute)
        elif self.outer_dfs_order == "state":
            ops.sort(key=lambda op : op.state)
        elif self.outer_dfs_order == "network":
            ops.sort(key=lambda op : op.network)
        elif not self.outer_dfs_order == "default":
            sys.exit("not gonna happen")

        # Print out the explore order
        print('======== OP explore order (outer DFS tree) ========')
        for op in reversed(ops):
            print(op.logicalOperatorName, " ", end="")
        print()

        return ops

    # Check the format of input physical execution graph
    def checkComputeG(self):
        l = len(self.numtasks)
        if (l < 2):
            sys.exit("Invalid compute graph: need at least 2 operators")

        totalSlots = self.workers_num * self.workers_slot
        submittedTaskNum = 0
        for op in self.numtasks.values():
            submittedTaskNum += op['parallelism']
            if op['state'] < 0 or op['state'] != op['state']:   # check NaN
                sys.exit("Invalid task I/O cost:", op['state'])
            if op['compute'] <= 0 or op['compute'] != op['compute']:
                sys.exit("Invalid task compute cost:", op['compute'])
            if op['network'] < 0 or op['network'] != op['network']:
                sys.exit("Invalid task network cost: negative cost:", op['network'])
        
        if submittedTaskNum > totalSlots:
            sys.exit("Number of submitted tasks > Number of available slots")

        return

    # Copy curPlace to get a snapshot of current task placements on all nodes
    # nodes is the strcuture used by inner DFS call stack
    # Each outer DFS layer will call buildNodeList() once
    # The length of nodes is the total num of physical nodes
    def buildNodeList(self, curPlace):
        nodes = []
        # TODO: find an order that minimize the search cost for each inner DFS. Now in the default map traversal order to construct the node list

        # default order
        for key in curPlace.map:
            val = curPlace.map[key]
            # Add all nodes
            for i in range(val.num):
                nodes.append(Node(key, copy.deepcopy(val.res), 0))

        # # re-order the inner dfs tree to enable early prunning
        # if self.outer_dfs_order == "compute":
        #     nodes.sort(key=lambda node : node.res.compute, reverse=True)
        # elif self.outer_dfs_order == "state":
        #     nodes.sort(key=lambda node : node.res.state, reverse=True)
        # elif self.outer_dfs_order == "network":
        #     nodes.sort(key=lambda node : node.res.network, reverse=True)
        # elif not self.outer_dfs_order == "default":
        #     sys.exit("not gonna happen")

        return nodes

    # Update curPlace at leaf node of each inner DFS call (to prepare next outer DFS layer)
    def updateCurPlace(self, nodes, op, curPlace):
        # Get a copy of current curPlace for backtrace purposes
        # Space complexity of this operatition is only O(# outer DFS layers = # of operator partition) -> usually constant
        oldCurPlace = copy.deepcopy(curPlace)
        # Update curPlace.leftSlots
        curPlace.leftSlots -= op.parallelism

        # Update curPlace.map using nodes operated by inner DFS
        map = {}
        if len(nodes) != self.workers_num:
            print("nodes list has incorrect # of workers")
            sys.exit(nodes)
        for node in nodes:
            # construct a new map based on nodes and pass it to curPlace.map
            newList = copy.deepcopy(node.key.list)
            for i in range(node.deployment):
                newList.append(op.logicalOperatorName)
            newList.sort()
            newKey = NodePlacement(newList)
            if (newKey in map):
                map[newKey].num += 1
            else:
                map[newKey] = NodePlacementInfo(1, node.res)
        
        curPlace.map = map
        return oldCurPlace

    # Backtrace curPlace when recursive outer DFS returns
    def backtraceCurPlace(self, curPlace, oldCurPlace):
        curPlace.leftSlots = oldCurPlace.leftSlots
        curPlace.map = oldCurPlace.map

    # Update node in nodes
    def updateNode(self, node, op, num):
        node.deployment = num
        # init nwcost caused by downstream link
        localnwcost = 0
        if num == 0:
            return localnwcost
        node.res.compute += op.compute * num
        node.res.state += op.state * num

        # update the network cost: only consider downstream cost here (upstream cost is handled at the end of each OP)
        downNodeList = op.downNode
        if len(downNodeList) > 1:
            sys.exit("current operator has multiple downstream operators: query type not accepted now (couldn't calculate network cost)")
        for downOp in downNodeList:     # only 1 in the list
            if downOp in self.deployedOps:
                downOpName = self.numtasks[downOp]['name']
                downOpPara = self.numtasks[downOp]['parallelism']
                # check how many downOp tasks are colocated on this node
                numDownOpDeployed = 0
                for taskname in node.key.list:     # node.key has NodePlacement type
                    if taskname == downOpName:
                        numDownOpDeployed += 1
                if op.outboundtype == 'forward':    # downstream link is 1-to-1: 0 cost if there are corresponding downstream tasks colocated on the same node
                    localnwcost += max(0, (num - numDownOpDeployed)) * op.network
                else:
                    localnwcost += (1 - numDownOpDeployed/downOpPara) * op.network * num
        node.res.network += localnwcost
        # return localnwcost for backtrace purposes
        return localnwcost

    # Backtrace node in nodes
    def backtraceNode(self, node, op, num, addedlocalnwcost):
        node.deployment = 0
        node.res.compute -= op.compute * num
        node.res.state -= op.state * num
        node.res.network -= addedlocalnwcost

    # Calculate thresholds for different resources
    def calculateThreshold(self, workers_num, workers_slot):

        # get threshold for compute/io
        total_compute = 0
        total_state = 0
        for v in self.numtasks.values():
            total_compute += v['parallelism'] * v['compute']
            total_state += v['parallelism'] * v['state']

        computeOptimal = total_compute / workers_num
        self.threshold_compute = computeOptimal * self.threshold_ratio.compute
        stateOptimal = total_state / workers_num
        self.threshold_state = stateOptimal * self.threshold_ratio.state

        # get threshold for network (ratio is <= 1, we can only calculate worst network cost)
        opList = []
        for value in self.numtasks.values():
            opList.append({'parallelism':value['parallelism'], 'nwcost':value['network']})
        opList.sort(key = lambda x:x['nwcost'], reverse=True)       # select tasks with higher nwcost first
        max_network_cost = 0        # get upper bound for node network cost
        for op in opList:
            numTaskToDeploy = min(workers_slot, op['parallelism'])
            max_network_cost += numTaskToDeploy * op['nwcost']
            workers_slot -= numTaskToDeploy
            if (workers_slot <= 0):
                break
        self.threshold_network = max_network_cost * self.threshold_ratio.network

        # print
        print("======== Cost threshold ========")
        print("Compute threshold:", self.threshold_compute, "Optimal:", computeOptimal, "Ratio:", self.threshold_ratio.compute)
        print("IO threshold:", self.threshold_state, "Optimal:", stateOptimal, "Ratio:", self.threshold_ratio.state)
        print("Network threshold:", self.threshold_network, "Worst:", max_network_cost, "Ratio:", self.threshold_ratio.network)

    # Get paretoOptimal plans from generated plans
    def getParetoOptimalPlans(self, plans):
        if len(plans) == 0:
            return plans

        # calculate cost for each plan
        plan_with_costs = []
        for plan in plans:
            max = ResourceUsage(0,0,0)
            for value in plan.values():
                max.getMax(value.res)
            plan_with_costs.append((plan, max))

        # get pareto optimal plans among all plans: naive n^2 solution
        pareto_optimal = []
        for p in plan_with_costs:
            opt = True
            for other_p in plan_with_costs:
                if p is other_p:
                    continue
                if p[1].isDominated(other_p[1]):
                    opt = False
                    break
            if opt:
                pareto_optimal.append(p[0])

        return pareto_optimal

    ############################# Outer DFS #############################

    def outerDFS(self, ops, curPlace, plans):
        # Trace outer tree size
        self.Outer_tree_node += 1
        # Successfully placed all tasks
        if(len(ops) == 0):
            plans.append( copy.deepcopy(curPlace.map) )
            if self.findBound:
                raise HasAvailablePlan("Has available plan at the current ratio -> abort search")
            return
        op = ops.pop()

        # Prepare node list for this op
        nodes = self.buildNodeList(curPlace)
        # Call inner DFS
        self.innerDFS(0, nodes, op.parallelism, curPlace.leftSlots, op, None, -1, ops, curPlace, plans)
        ops.append(op)

    ############################# Inner DFS #############################

    def innerDFS(self, index, nodes, leftTasks, leftSlots, op, lastNodeType, baseSlot, ops, curPlace, plans):
        # Trace inner tree size
        self.Inner_tree_node += 1
        if (leftTasks == 0):    # all tasks of this OP are placed
            if (index < len(nodes) and nodes[index].key == lastNodeType):
                return
            
            # Done placing the current op --> check if the upstream ops are already placed
            upNodeList = op.upNode
            deployedUpNodeList = []
            # print(op.logicalOperatorName, upNodeList)
            for upOp in upNodeList:
                if upOp in self.deployedOps:
                    deployedUpNodeList.append(upOp)

            # We have upstream ops deployed
            localnwcosts = [0] * len(nodes)
            if len(deployedUpNodeList) != 0:
                i = 0
                for n in nodes:
                    localnwcost = 0
                    numDownOpDeployed = n.deployment
                    downOpPara = op.parallelism
                    for upOp in deployedUpNodeList:
                        upOpName = self.numtasks[upOp]['name']
                        upOpnwcost = self.numtasks[upOp]['network']
                        numUpOpDeployed = 0
                        for taskName in n.key.list:
                            if taskName == upOpName:
                                numUpOpDeployed += 1
                        if self.numtasks[upOp]['outboundtype'] == 'forward':
                            localnwcost += max(0, (numUpOpDeployed - numDownOpDeployed)) * upOpnwcost
                        else:
                            localnwcost += (1 - numDownOpDeployed/downOpPara) * upOpnwcost * numUpOpDeployed

                    # check localnwcost
                    if (n.res.network + localnwcost > self.threshold_network):
                        return
                    localnwcosts[i] = localnwcost
                    i+=1

                # now update nodes nwcost
                for i, n in enumerate(nodes):
                    n.res.network += localnwcosts[i]
            
            # Update for next OP
            oldCurPlace = self.updateCurPlace(nodes, op, curPlace)
            self.deployedOps.add(op.logicalOperatorId)

            # Now explore next OP
            self.outerDFS(ops, curPlace, plans)

            #  Backtrace
            self.backtraceCurPlace(curPlace, oldCurPlace)
            self.deployedOps.remove(op.logicalOperatorId)
            for i, n in enumerate(nodes):       # now backtrace nodes on upstream nwcost
                n.res.network -= localnwcosts[i]
            
            return
        
        # Set up lower and upper bound of task placements on local node
        # num of available slots on this node
        slots = self.workers_slot - len(nodes[index].key.list)
        atMost = leftTasks
        if (slots < leftTasks):
            atMost = slots
        diff = leftTasks - (leftSlots - slots)
        atLeast = diff
        if (diff < 0):
            atLeast = 0
        # Check duplicate node and remove duplicate branches
        if (nodes[index].key == lastNodeType):
            if (atMost < baseSlot):
                return
            elif (baseSlot > atLeast):
                atLeast = baseSlot
        # Now explore all possible placement at this node
        for num in range(atLeast, atMost+1):
            # Update nodes
            addedlocalnwcost = self.updateNode(nodes[index], op, num)

            # Branch pruning on a local node placement of current OP：
            
            # (1) Cost Filter: compute (expected busy time)
            if (nodes[index].res.compute > self.threshold_compute):
                self.backtraceNode(nodes[index], op, num, addedlocalnwcost)
                break

            # (2) Cost Filter: I/O (iowrite + ioread)
            if (nodes[index].res.state > self.threshold_state):
                self.backtraceNode(nodes[index], op, num, addedlocalnwcost)
                break

            # (3) Cost Filter: network (ourbound traffic)
            if (nodes[index].res.network > self.threshold_network):
                self.backtraceNode(nodes[index], op, num, addedlocalnwcost)
                break

            self.innerDFS(index+1, nodes, leftTasks-num, leftSlots-slots, op, nodes[index].key, num, ops, curPlace, plans)
            # Backtrace nodes
            self.backtraceNode(nodes[index], op, num, addedlocalnwcost)

    ############################# Test #############################

    def testPlanCostCorrectness(self, plan):

        # each plan has the structure of curPlace.map
        for k, v in plan.items():
            # calculate compute, state
            cpcost = 0
            iocost = 0
            nwcost = 0
            placementList = k.list
            generatedRes = v.res

            taskCounts = {}     # keyed by op id not name

            for taskName in placementList:
                for key, value in self.numtasks.items():
                    if taskName == value['name']:
                        taskCounts[key] = taskCounts.get(key, 0) + 1
                        cpcost += value['compute']
                        iocost += value['state']
                        break
                
            # calculate network
            for key, num in taskCounts.items():
                value = self.numtasks[key]
                downOps = value['downNode']
                if len(downOps) > 1:
                    sys.exit("down op only support 1 now")
                for downOp in downOps:
                    downOpNum = 0
                    downOpName = self.numtasks[downOp]['name']
                    downOpPara = self.numtasks[downOp]['parallelism']
                    for localName in placementList:
                        if localName == downOpName:
                            downOpNum += 1
                    if value['outboundtype'] == 'forward':
                        nwcost += max(0, (num - downOpNum)) * value['network']
                    else:
                        nwcost += (1 - downOpNum/downOpPara) * value['network'] * num

            if not (almost_equal(cpcost, generatedRes.compute) and almost_equal(iocost, generatedRes.state) and almost_equal(nwcost, generatedRes.network)):
                print("!!!!!!!")
                print(cpcost, generatedRes.compute)
                print(iocost, generatedRes.state)
                print(nwcost, generatedRes.network)
                return False

        return True

    ############################# Main #############################

    def process(self):
        # Measure runtime
        start = time.time()

        # convert JobGarph to numtasks
        for gn in self.JobGraph.nodes.items():
            parallelism = nx.get_node_attributes(self.JobGraph, 'optimalparallelism')
            pname = nx.get_node_attributes(self.JobGraph, 'pname')
            # cost
            state = nx.get_node_attributes(self.JobGraph, 'iocost')
            compute = nx.get_node_attributes(self.JobGraph, 'cpcost')
            network = nx.get_node_attributes(self.JobGraph, 'nwcost')
            # outbound link pattern (for network): 'forward' and others
            outboundtype = nx.get_node_attributes(self.JobGraph, 'outboundtype')

            # get downstream op and upstream op
            downNode = list(self.JobGraph.neighbors(gn[0]))
            upNode = list(self.JobGraph.predecessors(gn[0]))

            # key and 'name' all should be unique. NodePlacement key is the name string
            self.numtasks[gn[0]] = {'name':pname[gn[0]], 'parallelism':parallelism[gn[0]], 'state':state[gn[0]], 'compute': compute[gn[0]],
                            'network': network[gn[0]], 'outboundtype': outboundtype[gn[0]], 'downNode': downNode, 'upNode': upNode}

        # Validate the computation graph structure
        self.checkComputeG()

        # Calculate threshold for resources
        self.calculateThreshold(self.workers_num, self.workers_slot)

        # Construct the operator partition stack for outer DFS
        ops = self.initStack()

        # Initialize the CurPlace structure
        curPlace = CurPlace(self.workers_num, self.workers_slot)

        # Resulting placement plans
        plans = []

        # Start from outerDFS
        self.outerDFS(ops, curPlace, plans)

        # Measure runtime
        end = time.time()
        dfsRuntime = end - start

        # Return all pareto optimal plans
        start = time.time()
        optimals = self.getParetoOptimalPlans(plans)
        end = time.time()
        paretoRuntime = end - start

        # Resulting placement plans
        print("======== DFS results statistics ========")
        print("Total num of possible plans:", len(plans))
        print("Total num of pareto optimal plans:", len(optimals))
        print("Outer tree size:", self.Outer_tree_node)
        print("Inner tree size:", self.Inner_tree_node)
        print("Pareto Optimal Runtime:", paretoRuntime)
        print("DFS Runtime:", dfsRuntime)

        # Plan cost correctness check
        if self.TESTCOST:
            if len(plans) > 0:
                for plan in plans:
                    if not self.testPlanCostCorrectness(plan):
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        print("False cost calculation! System aborts! Go check your algorithm!")
                        print(plan)
                        sys.exit()
                print("(All generated plans pass the cost correctness check!!)")

        # it returns both pareto optimals and all plans
        return(optimals, plans)






def testdfs(graphFile=None, compute_threshold_ratio=100, state_threshold_ratio=100, network_threshold_ratio=1, outer_dfs_order="default", _oi=0):
    ################# Input parameters
    writecfg=False
    # worker ips
    workers_ip=['192.168.1.8', '192.168.1.9', '192.168.1.12', '192.168.1.13']
    workers_num = len(workers_ip)
    # num of slots per worker
    workers_slot=8

    # threshold ratio
#     compute_threshold_ratio = 1.5       # optimal value * ratio: 1.0 going up to relax the requirement
#     state_threshold_ratio = 1.7         # optimal value * ratio: 1.0 going up to relax the requirement
#     network_threshold_ratio = 0.5         # worst value * ratio: 1.0 going down to tight the requirement
    ratio = ThresholdRatio(compute_threshold_ratio, state_threshold_ratio, network_threshold_ratio)

    # output config file name
    config_file_name = 'schedulercfg'


    JobGraph = None
    if graphFile == None:
        # computation graph
        JobGraph = nx.DiGraph()
        JobGraph.add_nodes_from([
            ('sink', {'parallelism': 1, 'optimalparallelism': 1, 'name': 'Sink', 'pname': 'Sink', 'cpcost': 1, 'nwcost': 0, 'iocost': 0, 'outboundtype':'others',  'innodes': ['a'], 'oip': 706197, 'oop': 0.0, 'tip': 6895336, 'top': 0.0, 'busytime': 102, 'bkpstime': 0.0, 'idletime': 897, 'selectivity': 0.0, 'ioread': 0.0, 'iowrite': 0.0, 'oib': 29308469, 'oob': 0.0}),
            ('window', {'parallelism': 7, 'optimalparallelism': 5, 'name': 'Window', 'pname': 'Window', 'cpcost': 5, 'nwcost': 20, 'iocost': 300, 'outboundtype':'others', 'innodes': ['b', 'a7656bc88070ceb7fdbe4bea9f8054df'], 'oip': 206834, 'oop': 7059326, 'tip': 417084, 'top': 1423525, 'busytime': 495, 'bkpstime': 11.0, 'idletime': 493, 'selectivity': 3, 'ioread': 10701960511, 'iowrite': 24773042170, 'oib': 46057984, 'oob': 29298958}),
            ('transP', {'parallelism': 1, 'optimalparallelism': 1, 'name': 'TransformPersons', 'pname': 'TransformPersons', 'cpcost': 2, 'nwcost': 40, 'iocost': 0, 'outboundtype':'others', 'innodes': ['c'], 'oip': 46000.0, 'oop': 46000, 'tip': 130280, 'top': 130280, 'busytime': 353, 'bkpstime': 0.0, 'idletime': 646, 'selectivity': 1.0, 'ioread': 0.0, 'iowrite': 0.0, 'oib': 10230879, 'oob': 9406417}),
            ('sourceP', {'parallelism': 1, 'optimalparallelism': 1, 'name': 'SourcePersons', 'pname': 'SourcePersons', 'cpcost': 1, 'nwcost': 5, 'iocost': 0, 'outboundtype':'others', 'innodes': [], 'oip': 0.0, 'oop': 46000.0, 'tip': 0, 'top': 46000, 'busytime': -1.0, 'bkpstime': 5, 'idletime': 0.0, 'selectivity': 0.0, 'ioread': 0.0, 'iowrite': 0.0, 'oib': 0.0, 'oob': 10230715}),
            ('transA', {'parallelism': 4, 'optimalparallelism': 4, 'name': 'TransformAuctions', 'pname': 'TransformAuctions', 'cpcost': 3, 'nwcost': 20, 'iocost': 0, 'outboundtype':'others', 'innodes': ['d'], 'oip': 161020, 'oop': 161020, 'tip': 295067, 'top': 295067, 'busytime': 545, 'bkpstime': 2.5, 'idletime': 451, 'selectivity': 1.0, 'ioread': 0.0, 'iowrite': 0.0, 'oib': 79982903, 'oob': 36694332}),
            ('sourceA', {'parallelism': 2, 'optimalparallelism': 4, 'name': 'SourceAuctions', 'pname': 'SourceAuctions', 'cpcost': 1, 'nwcost': 10, 'iocost': 0, 'outboundtype':'forward', 'innodes': [], 'oip': 0.0, 'oop': 161000, 'tip': 0, 'top': 161000, 'busytime': -1.0, 'bkpstime': 0.0, 'idletime': 0.0, 'selectivity': 0.0, 'ioread': 0.0, 'iowrite': 0.0, 'oib': 0.0, 'oob': 79971395.5}),
        ])
        JobGraph.add_edge('sourceP', 'transP')
        JobGraph.add_edge('sourceA', 'transA')
        JobGraph.add_edge('transP', 'window')
        JobGraph.add_edge('transA', 'window')
        JobGraph.add_edge('window', 'sink')
    else:
        JobGraph = pickle.load(open(graphFile, "rb"))

    dfsproc=DFSprocess(workers_num, workers_slot, ratio, JobGraph, outer_dfs_order)
    optimals, plans=dfsproc.process()

    # Generate placement config file
    if (len(optimals) == 0):
        print("no available placement plans")
    else:
        print("======== Placement plan found: ========")
        print(optimals[_oi])
        print("======== config_file_name: "+config_file_name, "========")
        workerIdx = 0
        if(writecfg):
            f = open(config_file_name, "w")
        for k,v in optimals[_oi].items():
            for i in range(v.num):
                for task in k.list:
                    ff=task+"; "+workers_ip[workerIdx]
                    print(ff)
                    if(writecfg):
                        f.write(ff+"\n")
                workerIdx+=1
        if(writecfg):
            f.close()


def testMicroBenchmark(graphFile):
    JobGraph = pickle.load(open(graphFile, "rb"))
    workers_ip=['192.168.1.8', '192.168.1.9', '192.168.1.12', '192.168.1.13']
    workers_slot = 8
    paras = MicrobenchmarkParas(1, 0.01, 0.1, 0.1)
    randomOptimal = True

    start = time.time()
    plan = microBenchmark(workers_ip, workers_slot, paras, randomOptimal, JobGraph)
    # plan = oldmicroBenchmark(workers_ip, workers_slot, paras, randomOptimal, JobGraph)
    end = time.time()

    print("======== Placement plan found:")
    print(plan)
    print("======== config_file ========")
    workerIdx = 0
    for k,v in plan.items():
        for i in range(v.num):
            for task in k.list:
                ff=task+"; "+workers_ip[workerIdx]
                print(ff)
            workerIdx+=1

    print()
    print("Micro-benchmark runtime:", end-start)
    print()


def microBenchmark(workers_ip, workers_slot, paras, randomOptimal, JobGraph):

    workers_num = len(workers_ip)

    # Check on graph costs
    totalIO = checkJobGraphMicroBenchmark(JobGraph)

    bigStep = 0.2      # step used to find the binary search bound
    loopLimit = 10      # loop limit to find the binary search bound
    decimals = 2    # granularity of dimension ratio is 0.01
    multiplier = 10 ** decimals
    step = 1 / multiplier

    compute_bound = 1
    state_bound = 1
    network_bound = 1

    # Measure time to find the bound
    start = time.time()

    # explore compute bound
    compute_trace = []
    loop = 0
    ratio = ThresholdRatio(1, 100, 1)
    upperBound = 1
    lowerBound = 1
    while loop<loopLimit:
        compute_trace.append(ratio.compute)
        dfsproc=DFSprocess(workers_num, workers_slot, ratio, JobGraph, "compute", findBound=True)
        # dfsproc=DFSprocess(workers_num, workers_slot, ratio, JobGraph, "default", findBound=True)
        try:
            optimals, plans=dfsproc.process()
        except HasAvailablePlan as e:
            compute_bound = ratio.compute
            upperBound = ratio.compute - step
            break
        lowerBound = ratio.compute + step
        ratio.compute += bigStep
        loop+=1

    if loop >= loopLimit:
        sys.exit("no bound found for compute")

    # Now we have the lower and upper bound
    print("compute lower bound:", lowerBound)
    print("compute upper bound", upperBound)

    while lowerBound <= upperBound:
        midWorks = False
        # get mid: keep decimals # places and round down
        ratio.compute = math.floor( round_if_close((lowerBound + upperBound)/2 * multiplier) ) / multiplier
        compute_trace.append(ratio.compute)
        dfsproc=DFSprocess(workers_num, workers_slot, ratio, JobGraph, "compute", findBound=True)
        # dfsproc=DFSprocess(workers_num, workers_slot, ratio, JobGraph, "default", findBound=True)
        try:
            optimals, plans=dfsproc.process()
        except HasAvailablePlan as e:
            # mid generates plans -> change upper bound
            compute_bound = ratio.compute
            upperBound = ratio.compute - step
            midWorks = True
        # mid no plans -> change lower bound
        if not midWorks:
            lowerBound = ratio.compute + step

    # explore state bound
    state_trace = []
    if totalIO == 0:        # no need to check if no cost on IO access
        state_bound = 1
    else:
        loop = 0
        ratio = ThresholdRatio(100, 1, 1)
        upperBound = 1
        lowerBound = 1
        while loop<loopLimit:
            state_trace.append(ratio.state)
            dfsproc=DFSprocess(workers_num, workers_slot, ratio, JobGraph, "state", findBound=True)
            # dfsproc=DFSprocess(workers_num, workers_slot, ratio, JobGraph, "default", findBound=True)
            try:
                optimals, plans=dfsproc.process()
            except HasAvailablePlan as e:
                state_bound = ratio.state
                upperBound = ratio.state - step
                break
            lowerBound = ratio.state + step
            ratio.state += bigStep
            loop+=1

        if loop >= loopLimit:
            sys.exit("no bound found for state")

        # Now we have the lower and upper bound
        print("state lower bound:", lowerBound)
        print("state upper bound", upperBound)

        while lowerBound <= upperBound:
            midWorks = False
            # get mid: keep decimals # places and round down
            ratio.state = math.floor( round_if_close((lowerBound + upperBound)/2 * multiplier) ) / multiplier
            state_trace.append(ratio.state)
            dfsproc=DFSprocess(workers_num, workers_slot, ratio, JobGraph, "state", findBound=True)
            # dfsproc=DFSprocess(workers_num, workers_slot, ratio, JobGraph, "default", findBound=True)
            try:
                optimals, plans=dfsproc.process()
            except HasAvailablePlan as e:
                # mid generates plans -> change upper bound
                state_bound = ratio.state
                upperBound = ratio.state - step
                midWorks = True
            # mid no plans -> change lower bound
            if not midWorks:
                lowerBound = ratio.state + step

    # explore network bound
    network_trace = []
    loop = 0
    ratio = ThresholdRatio(100, 100, 0.01)
    upperBound = 0.01
    lowerBound = 0.01
    while loop<loopLimit:
        network_trace.append(ratio.network)
        dfsproc=DFSprocess(workers_num, workers_slot, ratio, JobGraph, "network", findBound=True)
        # dfsproc=DFSprocess(workers_num, workers_slot, ratio, JobGraph, "default", findBound=True)
        try:
            optimals, plans=dfsproc.process()
        except HasAvailablePlan as e:
            network_bound = ratio.network
            upperBound = ratio.network - step
            break
        lowerBound = ratio.network + step
        ratio.network += bigStep
        loop+=1

    if loop >= loopLimit:
        sys.exit("no bound found for compute")

    # Now we have the lower and upper bound
    print("network lower bound:", lowerBound)
    print("network upper bound", upperBound)

    while lowerBound <= upperBound:
        midWorks = False
        # get mid: keep decimals # places and round down
        ratio.network = math.floor( round_if_close((lowerBound + upperBound)/2 * multiplier) ) / multiplier
        network_trace.append(ratio.network)
        dfsproc=DFSprocess(workers_num, workers_slot, ratio, JobGraph, "network", findBound=True)
        # dfsproc=DFSprocess(workers_num, workers_slot, ratio, JobGraph, "default", findBound=True)
        try:
            optimals, plans=dfsproc.process()
        except HasAvailablePlan as e:
            # mid generates plans -> change upper bound
            network_bound = ratio.network
            upperBound = ratio.network - step
            midWorks = True
        # mid no plans -> change lower bound
        if not midWorks:
            lowerBound = ratio.network + step


    end = time.time()
    findBoundTime = end - start

    # print(compute_trace)
    # print(state_trace)
    # print(network_trace)


    # Now relax the bound to get candidate placement plans (pareto optimal)
    # Relex the bound by defined percentage step over the bound on all dimensions
    # If # available plan found < threshold --> relax further by one more step

    # User defined parameters:
    # 1) At least how many plans are in the poll
    # 2) relax_step_ratio_compute: 10%
    # 3) relax_step_ratio_io: 10%
    # 4) relax_step_ratio_network: 10%

    optimals = []
    plans = []
    ratio = ThresholdRatio(compute_bound, state_bound, network_bound)
    loop = 0
    while loop<50:
        
        print("========== Micro-benchmark iteration", loop+1, "==========")
        print(f"  trying threshold ({ratio.compute}, {ratio.state}, {ratio.network})")

        # Now run dfs with relaxed threshold
        dfsproc=DFSprocess(workers_num, workers_slot, ratio, JobGraph, "compute")
        # dfsproc=DFSprocess(workers_num, workers_slot, ratio, JobGraph, "default")
        optimals, plans = dfsproc.process()
        
        print(f"  num of available plans: {len(plans)}")

        if len(plans)>=paras.planNum:
            break

        # no plans found -> relax all thresholds at the same time
        ratio.compute *= 1 + paras.step_ratio_compute
        ratio.state *= 1 + paras.step_ratio_io
        ratio.network *= 1 + paras.step_ratio_network
        if ratio.network > 1:
            ratio.network = 1

        loop += 1

    if loop >= 50:
        sys.exit("Relaxed 50 times and still no valid thresholds --> abort")

    print("========== Found valid ratio!! ==========")
    print(f"  # total plans: {len(plans)}")
    print(f"  # pareto optimal plans: {len(optimals)}")
    print(f"  micro-benchmark # iterations: {loop+1}")
    print(f"  valid ratio: ({ratio.compute}, {ratio.state}, {ratio.network})")
    print(f"  bound ratio: ({compute_bound}, {state_bound}, {network_bound})")
    print(f"  time used to find the bound: {findBoundTime}")
    plan = None
    if randomOptimal:
        print(f"  Randomly select the plan from the optimals")
        plan = random.choice(optimals)
    else:
        print(f"  Select the 1st plan from the optimals")
        plan = optimals[0]

    return plan


def oldmicroBenchmark(workers_ip, workers_slot, paras, randomOptimal, JobGraph):

    workers_num = len(workers_ip)

    # Check on graph costs
    totalIO = checkJobGraphMicroBenchmark(JobGraph)

    step = 0.01
    loopLimit = 1000
    compute_bound = 1
    state_bound = 1
    network_bound = 1

    # Measure time to find the bound
    start = time.time()

    # explore compute bound
    loop = 0
    ratio = ThresholdRatio(1, 100, 1)
    while loop<loopLimit:     
        dfsproc=DFSprocess(workers_num, workers_slot, ratio, JobGraph, "default", findBound=True)
        optimals = []
        plans = []
        try:
            optimals, plans=dfsproc.process()
        except HasAvailablePlan as e:
            compute_bound = ratio.compute
            break
        ratio.compute += step
        loop+=1
    if loop >= loopLimit:
        sys.exit("no bound found for compute")

    # explore state bound
    if totalIO == 0:        # no need to check if no cost on IO access
        state_bound = 1
    else:
        loop = 0
        ratio = ThresholdRatio(100, 1, 1)
        while loop<loopLimit:     
            dfsproc=DFSprocess(workers_num, workers_slot, ratio, JobGraph, "default", findBound=True)
            optimals = []
            plans = []
            try:
                optimals, plans=dfsproc.process()
            except HasAvailablePlan as e:
                state_bound = ratio.state
                break
            ratio.state += step
            loop+=1
        if loop >= loopLimit:
            sys.exit("no bound found for state")

    # explore network bound
    loop = 0
    ratio = ThresholdRatio(100, 100, 0.01)
    while loop<loopLimit:
        dfsproc=DFSprocess(workers_num, workers_slot, ratio, JobGraph, "default", findBound=True)
        optimals = []
        plans = []
        try:
            optimals, plans=dfsproc.process()
        except HasAvailablePlan as e:
            network_bound = ratio.network
            break
        ratio.network += step
        if ratio.network > 1:
            sys.exit("no bound found for network: ratio reach 1")
        loop+=1

    if loop >= loopLimit:
        sys.exit("no bound found for network")

    end = time.time()
    findBoundTime = end - start

    # Now relax the bound to get candidate placement plans (pareto optimal)
    # Relex the bound by defined percentage step over the bound on all dimensions
    # If # available plan found < threshold --> relax further by one more step

    # User defined parameters:
    # 1) At least how many plans are in the poll
    # 2) relax_step_ratio_compute: 10%
    # 3) relax_step_ratio_io: 10%
    # 4) relax_step_ratio_network: 10%

    optimals = []
    plans = []
    ratio = ThresholdRatio(compute_bound, state_bound, network_bound)
    loop = 0
    while len(plans)<paras.planNum and loop<100:
        ratio.compute *= 1 + paras.step_ratio_compute
        ratio.state *= 1 + paras.step_ratio_io
        ratio.network *= 1 + paras.step_ratio_network
        if ratio.network > 1:
            ratio.network = 1
        
        print("========== Micro-benchmark iteration", loop+1, "==========")
        print(f"  trying threshold ({ratio.compute}, {ratio.state}, {ratio.network})")

        # Now run dfs with relaxed threshold
        dfsproc=DFSprocess(workers_num, workers_slot, ratio, JobGraph, "default")
        optimals, plans = dfsproc.process()
        
        print(f"  num of available plans: {len(plans)}")
        loop += 1

    if loop >= 50:
        sys.exit("Relaxed 50 times and still no valid thresholds --> abort")

    print("========== Found valid ratio!! ==========")
    print(f"  # total plans: {len(plans)}")
    print(f"  # pareto optimal plans: {len(optimals)}")
    print(f"  micro-benchmark # iterations: {loop}")
    print(f"  valid ratio: ({ratio.compute}, {ratio.state}, {ratio.network})")
    print(f"  bound ratio: ({compute_bound}, {state_bound}, {network_bound})")
    print(f"  time used to find the bound: {findBoundTime}")
    plan = None
    if randomOptimal:
        print(f"  Randomly select the plan from the optimals")
        plan = random.choice(optimals)
    else:
        print(f"  Select the 1st plan from the optimals")
        plan = optimals[0]

    return plan