import pickle
import numpy as np
import pandas as pd
import sys, os

def custom_formatter(x):
    return f"{x:.2f}"

np.set_printoptions(threshold=np.inf, linewidth=np.inf, edgeitems=10)
np.set_printoptions(formatter={'all': custom_formatter})

optimalParaList = []

# Read and print job graph
def printJG(jgFile):
    jg=pickle.load(open(jgFile, 'rb'))
    for node, attrs in jg.nodes(data=True):

        # Operator id (key identifier)
        print("============ id ============")
        print(node)

        # Operator name
        print("============ pname ============")
        print(attrs['pname'])

        # Parallelism for the current (just finish) iteration
        print("============ parallelism ============")
        print(attrs['parallelism'])

        # Outbound link type
        print("============ outboundtype ============")
        print(attrs['outboundtype'])

        # List of data points for all past policy intervals

        # Observed input processing rate for the past intervals (all data points): sum of all subtask oip
        print("============ _oip ============")
        print(attrs['_oip'])

        # Observed output processing rate for the past intervals (all data points): sum of all subtask oop
        print("============ _oop ============")
        print(attrs['_oop'])

        # # Observed output rate per task
        # print("============ Per task _oop ============")
        # taskOOPList = []
        # for _pertaskdict in attrs['_pertask']:      # each element of attrs['_pertask'] is a interval data point: dataFrame containing task info for all metrics 
        #     taskOOPList.append(_pertaskdict['_oop'])
        # print(taskOOPList)

        # Observed output bytes rate for the past intervals (all data points): sum of all subtask oob
        print("============ _oob ============")
        print(attrs['_oob'])

        # # Observed output rate per task
        # print("============ Per task _oob ============")
        # taskOOPList = []
        # for _pertaskdict in attrs['_pertask']:      # each element of attrs['_pertask'] is a interval data point: dataFrame containing task info for all metrics 
        #     taskOOPList.append(_pertaskdict['_oob'])
        # print(taskOOPList)     

        # True input processing rate for the past intervals (all data points): sum of all subtask tip
        print("============ _tip ============")
        print(attrs['_tip'])

        # True output processing rate for the past intervals (all data points): sum of all subtask top
        print("============ _top ============")
        print(attrs['_top'])

        # Target input rate for the past intervals (all data points)
        print("============ _tips ============")
        print(attrs['_tips'])

        # Target output rate for the past intervals (all data points)
        print("============ _tops ============")
        print(attrs['_tops'])

        # Selectivity for the past itervals (all data points)
        print("============ _selectivity ============")
        print(attrs['_selectivity'])

        # Busy time for the past intervals (all data points): mean of all subtasks
        print("============ _busytime ============")
        print(attrs['_busytime'])

        # Backpressure time for the past intervals (all data points): mean of all subtasks
        print("============ _bkpstime ============")
        print(attrs['_bkpstime'])

        # cpu util of the taskmanager of the subtask: mean of all subtasks
        # average cpu util of all cores
        print("============ _cpuutil ============")
        print(attrs["_cpuutil"])

        # Calculated parallelism by DS2 for next iteration (each data point has a value)
        print("============ _optimalparallelism ============")
        print(attrs['_optimalparallelism'])

        # Timestamp
        if('_timestamp' in attrs.keys()):
            print("============ timestamp ============")
            print(attrs['_timestamp'])

        # After collecting all metrics: get mean values on all historical data

        # Average observed input rate
        print("============ oip ============")
        print(attrs['oip'])

        # Average observed output rate
        print("============ oop ============")
        print(attrs['oop'])

        # # Standard deviation of the oop rate
        # print("============ standard deviation oop ============")
        # print(np.std(attrs['_oop']))

        # Average true input rate
        print("============ tip ============")
        print(attrs['tip'])

        # Average true output rate
        print("============ top ============")
        print(attrs['top'])

        # Target input rate (mean but all the same)
        print("============ tips ============")
        print(attrs['tips'])

        # Target output rate (mean but all the same)
        print("============ tops ============")
        print(attrs['tops'])

        # Average busytime
        print("============ busytime ============")
        print(attrs['busytime'])

        # Average backpressure time
        print("============ bkpstime ============")
        print(attrs['bkpstime'])

        # Average cpu util
        print("============ cpuutil ============")
        print(attrs["cpuutil"])

        # Selectivity (mean but all the same)
        print("============ selectivity ============")
        print(attrs['selectivity'])

        # Ceil of the average optimal parallelism
        print("============ optimalparallelism ============")
        print(attrs['optimalparallelism'])

        # Max optimalparallelism value for all intervals
        print("============ maxoptimalparallelism ============")
        print(attrs['maxoptimalparallelism'])

        # Now print out cost
        print("============ cpcost, iocost, nwcost ============")
        print(attrs['cpcost'],attrs['iocost'],attrs['nwcost'])

        # print("----------- pertask -------------")
        # print(attrs['_pertask'])

        optimalParaList.append((attrs['pname'], attrs['optimalparallelism']))

        # unit cost per rec
        if("_cpcost" in attrs.keys()):
            print("============ _cpcost, _iocost, _nwcost ============")
            print(attrs['_cpcost'],attrs['_iocost'],attrs['_nwcost'])

        # # 
        print()
        print()
        print()

        # break

    totalslot = 0
    for pair in optimalParaList:
        print(f"{pair[0]}: {pair[1]}")
        totalslot += pair[1]
    print(f"Total required slots: {totalslot}")


ff=sys.argv[1]
printJG(ff)
