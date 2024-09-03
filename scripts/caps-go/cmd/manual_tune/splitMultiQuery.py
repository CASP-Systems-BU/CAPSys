import json

# Split the multi-query placement plan file into multiple files
# Each file corresponds to a single query

# Define all queries
Q1 = {}
Q1_ops = ["Q1_Sink", "Q1_SlidingWindow", "Q1_Transform", "Q1_Source"]

Q2 = {}
Q2_ops = ["Q2_SourceAuctions", "Q2_TransformAuctions", "Q2_SourcePersons", "Q2_TransformPersons", "TumblingEventTimeWindows", "Q2_Sink"]

Q3 = {}
Q3_ops = ["Q3_Source", "Q3_Transform", "Q3_Compress", "Q3_Inference", "Q3_Sink"]

Q4 = {}
Q4_ops = ["Q4_SourcePersons", "Q4_Filter", "Q4_SourceAuctions", "Q4_IncrementalJoin", "Q4_Sink"]

Q5 = {}
Q5_ops = ["Q5_SourceBid", "Q5_SourceAuction", "Q5_JoinBidsWithAuctions", "Q5_AggregateFunction", "Q5_Sink"]

Q6 = {}
Q6_ops = ["Q6_Source", "SessionWindow", "Q6_Sink"]


# Split lines in infile
input_file_path = 'schedulercfg'
infile = open(input_file_path, 'r')
schedulercfg_Q1 = []
schedulercfg_Q2 = []
schedulercfg_Q3 = []
schedulercfg_Q4 = []
schedulercfg_Q5 = []
schedulercfg_Q6 = []
for line in infile:

    for op in Q1_ops:
        if op in line:
            schedulercfg_Q1.append(line[1:-3])

    for op in Q2_ops:
        if op in line:
            schedulercfg_Q2.append(line[1:-3])

    for op in Q3_ops:
        if op in line:
            schedulercfg_Q3.append(line[1:-3])

    for op in Q4_ops:
        if op in line:
            schedulercfg_Q4.append(line[1:-3])

    for op in Q5_ops:
        if op in line:
            schedulercfg_Q5.append(line[1:-3])

    for op in Q6_ops:
        if op in line:
            schedulercfg_Q6.append(line[1:-3])


# Over-write placement plan in multi.json
multiJsonFilePath = "../../../expjson/multi.json"
multiJsonFile = open(multiJsonFilePath, 'r')
multiJson = json.load(multiJsonFile)


for index, job in enumerate(multiJson["jobs"]):
    # Q1
    if "Query5mod-jar-with-dependencies.jar" in job["jarpath"]:
        multiJson["jobs"][index]["schedulercfg1st"] = schedulercfg_Q1
    
    # Q2
    if "Query8mod-jar-with-dependencies.jar" in job["jarpath"]:
        multiJson["jobs"][index]["schedulercfg1st"] = schedulercfg_Q2
    
    # Q3
    if "FeedForwardPipeline-jar-with-dependencies.jar" in job["jarpath"]:
        multiJson["jobs"][index]["schedulercfg1st"] = schedulercfg_Q3

    # Q4
    if "Query3-jar-with-dependencies.jar" in job["jarpath"]:
        multiJson["jobs"][index]["schedulercfg1st"] = schedulercfg_Q4

    # Q5
    if "Query6-jar-with-dependencies.jar" in job["jarpath"]:
        multiJson["jobs"][index]["schedulercfg1st"] = schedulercfg_Q5

    # Q6
    if "Query11-jar-with-dependencies.jar" in job["jarpath"]:
        multiJson["jobs"][index]["schedulercfg1st"] = schedulercfg_Q6

with open(multiJsonFilePath, 'w') as file:
    json.dump(multiJson, file)