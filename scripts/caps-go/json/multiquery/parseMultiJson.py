import json

# Adjust the task cost value based on the actual target rate for the experiment
# Handle cases when profile target rate is different from actual deployments

# Define all queries
Deem = {}
Deem["Q3_Source"] = None
Deem["Q3_Transform"] = None
Deem["Q3_Compress"] = None
Deem["Q3_Inference"] = None
Deem["Q3_Sink"] = None
DeemProfileTargetRate = 9940
DeemActualTargetRate = 6960
DeemFactor = DeemActualTargetRate/DeemProfileTargetRate

Q8 = {}
Q8["Q2_SourceAuctions"] = None
Q8["Q2_TransformAuctions"] = None
Q8["Q2_SourcePersons"] = None
Q8["Q2_TransformPersons"] = None
Q8["TumblingEventTimeWindows"] = None
Q8["Q2_Sink"] = None
Q8ProfileTargetRate = 85000*10
Q8ActualTargetRate = 50000*10
Q8Factor = Q8ActualTargetRate/Q8ProfileTargetRate


input_file_path = "multi.json"
output_file_path = "multi_aligned.json"

file = open(input_file_path, 'r')
ops = json.load(file)

totalTask = 0
for op in ops:

    totalTask += op["parallelism"]

    # Operators of Deem
    if op["name"] in Deem:
        op["compute"] *= DeemFactor
        op["state"] *= DeemFactor
        op["network"] *= DeemFactor

    # Operators of Q8
    if op["name"] in Q8:
        op["compute"] *= Q8Factor
        op["state"] *= Q8Factor
        op["network"] *= Q8Factor

with open(output_file_path, 'w') as file:
    json.dump(ops, file, indent=2)


print("Total # tasks:", totalTask)

