import json
import pickle
import networkx as nx
import sys

# Input job graph files
# graphFiles = ["../../json/multiquery/pkl/q3.pkl", "../../json/multiquery/pkl/q5.pkl", "../../json/multiquery/pkl/q11.pkl", "../../json/multiquery/pkl/q8.pkl", "../../json/multiquery/pkl/deem.pkl"]
# graphFiles = ["/Users/geoffrey/Desktop/singlequery_16slot_cloudlab_profile/Q2/jg.pkl"]
graphFiles = ["/Users/geoffrey/Desktop/jg.pkl"]

# Final output
finalOps = []

# Starting id
id_base = ord('a') - 1


for graphFile in graphFiles:
    jobGraph = pickle.load(open(graphFile, "rb"))

    # Raw id to char id mapping
    rawIdToCharId = {}
    # Local output
    ops = []

    for gn in jobGraph.nodes.items():
        id_base += 1
        if id_base > ord('z'):
            sys.exit("Convert JG error: too many operators (# of operator exceeding z)")
        # manually assign id from a to z
        id = chr(id_base)
        rawIdToCharId[gn[0]] = id
        parallelism = nx.get_node_attributes(jobGraph, 'optimalparallelism')
        name = nx.get_node_attributes(jobGraph, 'pname')
        # cost
        state = nx.get_node_attributes(jobGraph, 'iocost')
        compute = nx.get_node_attributes(jobGraph, 'cpcost')
        network = nx.get_node_attributes(jobGraph, 'nwcost')
        # outbound link pattern (for network): 'forward' and others
        outboundtype = nx.get_node_attributes(jobGraph, 'outboundtype')
        # get downstream op and upstream op
        downNode = list(jobGraph.neighbors(gn[0]))
        upNode = list(jobGraph.predecessors(gn[0]))
        ops.append({'id':id, 'name':name[gn[0]], 'parallelism':parallelism[gn[0]], 'state':state[gn[0]], 'compute': compute[gn[0]],
                                'network': network[gn[0]], 'outboundtype': outboundtype[gn[0]], 'downNode': downNode, 'upNode': upNode})

    # convert raw id in down/up Node list to char id
    for op in ops:
        downNodeChar = []
        for e in op['downNode']:
            downNodeChar.append(rawIdToCharId[e])
        op['downNode'] = downNodeChar

        upNodeChar = []
        for e in op['upNode']:
            upNodeChar.append(rawIdToCharId[e])
        op['upNode'] = upNodeChar

    finalOps.extend(ops)

# with open('../../json/singlequery/deem_16_512.json', 'w') as file:
# with open('../../json/multiquery/multi.json', 'w') as file:
# with open('../../json/singlequery_cloudlab/Q5.json', 'w') as file:
with open('../../json/singlequery_8slot/Q5.json', 'w') as file:
    json.dump(finalOps, file)
    
