import json

# Note: change newTargetRate and replace "None" field

# Define all queries
queries = []
targetRateFactors = []

# Q1
query = {}
query["Q1_Sink"] = None
query["Q1_SlidingWindow"] = None
query["Q1_Transform"] = None
query["Q1_Source"] = None
oldTargetRate = 20000 * 1
newTargetRate = 18000 * 1
queries.append(query)
targetRateFactors.append(newTargetRate/oldTargetRate)

# Q2
# source auction rate : source people rate = 10
query = {}
query["Q2_Sink"] = None
query["TumblingEventTimeWindows"] = None
query["Q2_TransformPersons"] = None
query["Q2_SourcePersons"] = None
query["Q2_TransformAuctions"] = None
query["Q2_SourceAuctions"] = None
oldTargetRate = 50000 * 4
newTargetRate = 48000 * 4
queries.append(query)
targetRateFactors.append(newTargetRate/oldTargetRate)

# Q3
query = {}
query["Q3_Sink"] = None
query["Q3_Inference"] = None
query["Q3_Compress"] = None
query["Q3_Transform"] = None
query["Q3_Source"] = None
oldTargetRate = 600 * 5
newTargetRate = 570 * 5
queries.append(query)
targetRateFactors.append(newTargetRate/oldTargetRate)

# Q4
# source auction rate (10) : source people rate (3)
# This query shows high join cost after warmup (incremental join)
# need re-profile
query = {}
query["Q4_SourcePersons"] = None
query["Q4_Filter"] = None
query["Q4_SourceAuctions"] = None
query["Q4_IncrementalJoin"] = None
query["Q4_Sink"] = None
oldTargetRate = 70000 * 6
newTargetRate = 63000 * 6
queries.append(query)
targetRateFactors.append(newTargetRate/oldTargetRate)

# Q5
# source auction rate : source bid rate = 1
query = {}
query["Q5_SourceAuction"] = None
query["Q5_SourceBid"] = None
query["Q5_JoinBidsWithAuctions"] = None
query["Q5_AggregateFunction"] = None
query["Q5_Sink"] = None
oldTargetRate = 90000 * 2
newTargetRate = 60000 * 2
queries.append(query)
targetRateFactors.append(newTargetRate/oldTargetRate)

# Q6
query = {}
query["Q6_Source"] = None
query["SessionWindow"] = None
query["Q6_Sink"] = None
oldTargetRate = 72000 * 4
newTargetRate = 60000 * 4
queries.append(query)
targetRateFactors.append(newTargetRate/oldTargetRate)


input_file_path = "singlequery_8slot/Q5.json"
output_file_path = "singlequery_8slot/Q5_updated.json"


# Replace operator name for placement
opNameMapping = {}
# Q1
opNameMapping["Window_SlidingEventTimeWindows_3600000__60000___EventTimeTrigger__BidCountAggregate__AuctionWindowFunction_"] = "Q1_SlidingWindow"
opNameMapping["Source__Q1_Source___TimestampAssigner"] = "Q1_Source"
# Q2
opNameMapping["Window_TumblingEventTimeWindows_10000___EventTimeTrigger__CoGroupWindowFunction_"] = "TumblingEventTimeWindows"
opNameMapping["Q2_TransformPersons___Map"] = "Q2_TransformPersons"
opNameMapping["Source__Q2_SourcePersons___TimestampAssigner"] = "Q2_SourcePersons"
opNameMapping["Q2_TransformAuctions___Map"] = "Q2_TransformAuctions"
opNameMapping["Source__Q2_SourceAuctions___TimestampAssigner"] = "Q2_SourceAuctions"
# Q3
opNameMapping["Source__Q3_Source___TimestampAssigner"] = "Q3_Source"
# Q4
opNameMapping["Source__Q4_SourceAuctions"] = "Q4_SourceAuctions"
opNameMapping["Source__Q4_SourcePersons"] = "Q4_SourcePersons"
# Q5
opNameMapping["Window_TumblingEventTimeWindows_10000___EventTimeTrigger__AggregateFunction$4__PassThroughWindowFunction_"] = "Q5_AggregateFunction"
opNameMapping["Source__Q5_SourceAuction___TimestampAssigner"] = "Q5_SourceAuction"
opNameMapping["Source__Q5_SourceBid___TimestampAssigner"] = "Q5_SourceBid"
# Q6
opNameMapping["Window_EventTimeSessionWindows_10000___MaxLogEventsTrigger__CountBidsPerSession__PassThroughWindowFunction_"] = "SessionWindow"
opNameMapping["Source__Q6_Source___Timestamps/Watermarks"] = "Q6_Source"


file = open(input_file_path, 'r')
ops = json.load(file)

# Update all operator names first
for op in ops:
    if op['name'] in opNameMapping:
        op['name'] = opNameMapping[op['name']]

# Update cost and parallelism
totalTasks = 0
for op in ops:
    # Traverse all defined queries to find a match
    for index, query in enumerate(queries):

        # Find the matched query
        if op['name'] in query:
            # Update cost based on new target rate
            op["compute"] *= targetRateFactors[index]
            op["state"] *= targetRateFactors[index]
            op["network"] *= targetRateFactors[index]
            # Update parallelism and cost based on new parallelism
            newParallelism = query[op['name']]
            if not newParallelism is None:
                factor = op["parallelism"] / newParallelism
                op["compute"] *= factor
                op["state"] *= factor
                op["network"] *= factor
                op["parallelism"] = newParallelism
    totalTasks += op['parallelism']
    print(op['name'], op['parallelism'])

print("Total tasks:", totalTasks)

with open(output_file_path, 'w') as file:
    json.dump(ops, file)