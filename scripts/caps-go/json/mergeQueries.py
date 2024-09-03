import json


jsonFiles = ["singlequery_8slot/Q1_updated.json", "singlequery_8slot/Q2_updated.json", "singlequery_8slot/Q3_updated.json", "singlequery_8slot/Q4_updated.json", "singlequery_8slot/Q5_updated.json", "singlequery_8slot/Q6_updated.json"]
# jsonFiles = ["singlequery_cloudlab/Q1_updated.json" "singlequery_cloudlab/Q3_updated.json", "singlequery_cloudlab/Q4_updated.json", "singlequery_cloudlab/Q5_updated.json", "singlequery_cloudlab/Q6_updated.json"]

output_file_path = "mergedQuery.json"

# Print out total compute cost for each query
alignFactors = {}
alignFactors["singlequery_8slot/Q1_updated.json"] = 1
alignFactors["singlequery_8slot/Q2_updated.json"] = 1
alignFactors["singlequery_8slot/Q3_updated.json"] = 1
alignFactors["singlequery_8slot/Q4_updated.json"] = 1
alignFactors["singlequery_8slot/Q5_updated.json"] = 1
alignFactors["singlequery_8slot/Q6_updated.json"] = 1
# alignFactors["singlequery_cloudlab/Q1_updated.json"] = 1
# alignFactors["singlequery_cloudlab/Q3_updated.json"] = 1
# alignFactors["singlequery_cloudlab/Q4_updated.json"] = 1
# alignFactors["singlequery_cloudlab/Q5_updated.json"] = 1
# alignFactors["singlequery_cloudlab/Q6_updated.json"] = 1


# Print out total compute cost for all queries
for jsonFile in jsonFiles:
    file = open(jsonFile, 'r')
    ops = json.load(file)
    totalCPUcost = 0
    for op in ops:
        totalCPUcost += op["compute"] * op["parallelism"]
    print(jsonFile, "===", totalCPUcost)


# Merge json files for multi-query experiment
id_base = ord('a')
mergedOps = []
totalTasks = 0
for jsonFile in jsonFiles:
    file = open(jsonFile, 'r')
    ops = json.load(file)
    queryTasks = 0
    print("===================", jsonFile)
    # Replace operator id based on id_base
    for op in ops:
        print(op["name"],op["parallelism"])
        queryTasks += op["parallelism"]
        # Replace id
        op["id"] = chr(ord(op["id"]) - ord('a') + id_base)
        # Replace upstream op
        newUpNode = []
        for upnode in op["upNode"]:
            newUpNode.append(chr(ord(upnode) - ord('a') + id_base))
        op["upNode"] = newUpNode
        # Replace downstream op
        newDownNode = []
        for downnode in op["downNode"]:
            newDownNode.append(chr(ord(downnode) - ord('a') + id_base))
        op["downNode"] = newDownNode

        # Align cost when considering all queries
        op["compute"] *= alignFactors[jsonFile]

    mergedOps.extend(ops)
    totalTasks += queryTasks
    print("# tasks of this query:", queryTasks)

    # Increment base
    id_base += len(ops)

# Write to the merged file
with open(output_file_path, 'w') as file:
    json.dump(mergedOps, file)

print()
print("Total tasks:", totalTasks)



