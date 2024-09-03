package main

import (
	"encoding/json"
	"fmt"
	"math"
	"os"
	"strconv"
	"strings"
	"time"

	"casp.system.bu/placement/caps_multi"
)

/*
This script is for Section 6.4 CAPS_only experiments (Figure 10 left). The selected query
for this experiment is Q2-join.

Cluster setup: we fix the number of workers to be 4, and configure the number of slots per
worker to be 4, 8, 16, 32, 48, 64. Therefore, there are 6 problem sizes (# of tasks)
evaluated in the experiment: 16, 32, 64, 128, 196, 256 tasks. The query profile (parallelism
and cost) is propotionally updated for each setup to fulfill the available slots in the cluster.

Threshold setup: we select 3 groups of representative threshold for the experiments.
(1)	α(0.08, 0.15, 0.6)
(2) α(0.15, 0.25, 0.8)
(3) α(0.25, 0.3, 0.9)

Procedure: For each threshold and number of slots configuration, we invoke CAPS to measure
its runtime until the 1st satisfactory placement plan is found. We log the measured runtime
into a file for visualization later.
*/

func main() {

	// Define the cluster configurations
	num_workers := []int{4}
	num_slots := []int{4, 8, 16, 32, 48, 64}

	// Define 3 representative thresholds
	thresholds := []*caps_multi.ThresholdRatio{
		{
			Compute: 0.08,
			State:   0.15,
			Network: 0.6,
		},
		{
			Compute: 0.15,
			State:   0.25,
			Network: 0.8,
		},
		{
			Compute: 0.25,
			State:   0.3,
			Network: 0.9,
		},
	}

	// Profile file names
	source_json_file := "Q2_original_profile.json"
	new_json_file := "Q2_updated_profile.json"

	// Read Q2-join profile
	bytes, err := os.ReadFile(source_json_file)
	if err != nil {
		fmt.Println("Convert json format Error reading file:", err)
		os.Exit(1)
	}
	// Decode the json object
	var ops []map[string]interface{}
	err = json.Unmarshal(bytes, &ops)
	if err != nil {
		fmt.Println("Convert json format Error unmarshalling JSON:", err)
		os.Exit(1)
	}

	// Proportionally scale up the job as the original job graph
	total_tasks := float64(0)
	op_paras := []float64{}
	op_proportions := []float64{}
	// Get total tasks
	for _, op := range ops {
		// convert parallelism to int
		para_float, ok := op["parallelism"].(float64)
		if !ok {
			fmt.Println("Convert json format Error: The value is not a number")
			os.Exit(1)
		}
		op_paras = append(op_paras, para_float)
		total_tasks += para_float
	}
	// Get proportional tasks
	for _, op_para := range op_paras {
		op_proportions = append(op_proportions, op_para/total_tasks)
	}

	// Init CAPS paras
	parameterCAPS := &caps_multi.ParameterCAPS{
		JobGraph_jsonFile: new_json_file,
		ExitOnFirstPlan:   true,
		ExitOnTimeOut:     true,
		Outer_dfs_order:   "compute",
		ThreadNum:         38,
		// Timeout interval if earlyExit is true
		Timeout: 500 * time.Millisecond,
		// Result processing parameters
		CalculateParetoPlans:     false,
		SelectPlanAndWriteToFile: false,                                                                  // used when calculate pareto, if write plan to config file
		IpList:                   []string{"192.168.1.8", "192.168.1.9", "192.168.1.12", "192.168.1.13"}, // used when WriteToFile is true
		Config_file_name:         "schedulercfg",                                                         // used when WriteToFile is true
		TestCostCorrectness:      false,
	}

	// Traverse 3 thresholds
	res_runtime := [][]time.Duration{}
	findplansornots := [][]bool{}
	for threshold_idx, threshold := range thresholds {
		parameterCAPS.Threshold_ratio = threshold

		res_runtime = append(res_runtime, []time.Duration{})
		findplansornots = append(findplansornots, []bool{})

		fmt.Printf("******************** Try threshold (%f, %f, %f)\n", threshold.Compute, threshold.State, threshold.Network)

		// Traverse different cluster setups
		for _, num_worker := range num_workers {
			for _, num_slot := range num_slots {

				fmt.Printf("******************** Worker: %d, Slot: %d\n", num_worker, num_slot)

				// Total slots for current setup
				total_slots := num_worker * num_slot

				// Assign the updated parallelism and let total # tasks == # slots
				left_slots := total_slots
				for i := range ops {
					if i == len(ops)-1 {
						ops[i]["parallelism"] = left_slots // assign rest slots to the last op
					} else {
						tasks_to_deploy := int(math.Floor(op_proportions[i] * float64(total_slots)))
						if tasks_to_deploy == 0 {
							tasks_to_deploy = 1
						}
						left_slots -= tasks_to_deploy
						ops[i]["parallelism"] = tasks_to_deploy
					}
				}

				// Convert the updated records back to JSON
				updatedData, err := json.MarshalIndent(ops, "", "    ")
				if err != nil {
					fmt.Println("Error marshaling JSON:", err)
					return
				}

				// Write the JSON data to the file
				err = os.WriteFile(new_json_file, updatedData, 0644) // 0644 specifies the file permissions
				if err != nil {
					fmt.Println("Error writing JSON to file:", err)
					return
				}

				// Update the paras
				parameterCAPS.WorkerNum = num_worker
				parameterCAPS.SlotNum = num_slot

				minDuration := time.Duration(1<<63 - 1)
				findplanornot := false
				for k := 0; k < 1; k++ {
					fmt.Println("==== iteration", k+1, "====")
					startTime := time.Now()
					findplanornot = caps_multi.RunCAPS(parameterCAPS) || findplanornot
					endTime := time.Now()
					runtime := endTime.Sub(startTime)
					if runtime < minDuration {
						minDuration = runtime
					}
				}
				findplansornots[threshold_idx] = append(findplansornots[threshold_idx], findplanornot)
				res_runtime[threshold_idx] = append(res_runtime[threshold_idx], minDuration)

			}
		}

		fmt.Println()
	}

	// Print the results
	for threshold_idx, threshold := range thresholds {
		fmt.Printf("  Threshold (%f, %f, %f)\n", threshold.Compute, threshold.State, threshold.Network)
		idx := 0
		for _, num_worker := range num_workers {
			for _, num_slot := range num_slots {
				// fmt.Println(num_worker, "worker *", num_slot, "slot:", res_runtime[threshold_idx][idx], "FindPlan?", findplansornots[threshold_idx][idx])
				fmt.Println(num_worker, "worker *", num_slot, "slot:", res_runtime[threshold_idx][idx])
				idx += 1
			}
		}
		fmt.Println()

		// Write into file
		result_file_name := "result_threshold_" + strconv.Itoa(threshold_idx)
		var durationStrings []string
		for _, d := range res_runtime[threshold_idx] {
			durationStrings = append(durationStrings, d.String())
		}
		data := strings.Join(durationStrings, "\n") + "\n"
		err := os.WriteFile(result_file_name, []byte(data), 0644)
		if err != nil {
			fmt.Println("Error writing to file:", err)
			return
		}
	}

}
