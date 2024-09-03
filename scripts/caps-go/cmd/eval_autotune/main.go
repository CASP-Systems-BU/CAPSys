package main

import (
	"encoding/json"
	"fmt"
	"math"
	"os"
	"time"

	"casp.system.bu/placement/caps_multi"
)

func main() {

	num_workers := []int{8, 10, 12, 14, 16}
	num_slots := []int{4, 8, 16, 32, 64}

	source_json_file := "Q2_original_profile.json"
	new_json_file := "Q2_updated_profile.json"

	// Read json file
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

	// Init caps paras
	parameterCAPS := &caps_multi.ParameterCAPS{
		JobGraph_jsonFile:        new_json_file,
		WorkerNum:                4,
		SlotNum:                  4,
		Outer_dfs_order:          "compute",
		ThreadNum:                38,
		SelectPlanAndWriteToFile: false,
		IpList:                   []string{"192.168.1.8", "192.168.1.9", "192.168.1.12", "192.168.1.13"},
		Config_file_name:         "schedulercfg",
		TestCostCorrectness:      false,
	}
	// Init autotune paras
	parameterAutoTune := &caps_multi.ParameterAutoTune{
		// Search range
		ComputeCeiling: 0.07,
		StateCeiling:   0.07,
		NetworkCeiling: 0.5,
		// Search granularity
		Granularity: 0.01,
		// Relax rate
		AutoTuneRate: 0.2,
		// Timeout intervals
		CeilingRelaxTimeout: 500 * time.Millisecond,
		Phase1Timeout:       500 * time.Millisecond,
		Phase2Timeout:       5 * time.Second,
		// Number of CAPS repeat
		NumRepeatSearch: 15,
		NumRepeatResult: 10,
	}

	var tasks []int
	var seconds []float64
	for _, num_worker := range num_workers {
		for _, num_slot := range num_slots {
			// text = fmt.Sprintf("[Benchmark] Evaluate %d workers * %d slot", num_worker, num_slot)
			// WriteLog(writer, text)
			fmt.Printf("[***Benchmark***] Evaluate %d workers * %d slot\n", num_worker, num_slot)

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

			// Update the autotune paras
			parameterCAPS.WorkerNum = num_worker
			parameterCAPS.SlotNum = num_slot

			// Evaluate
			startTime := time.Now()
			caps_multi.Auto_tuning(parameterCAPS, parameterAutoTune)
			endTime := time.Now()
			runtime := endTime.Sub(startTime)
			tasks = append(tasks, num_worker*num_slot)
			seconds = append(seconds, runtime.Seconds())
		}
	}

	// Write data points into file
	file, err := os.OpenFile("result", os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0644)
	if err != nil {
		fmt.Println("Error opening file:", err)
		return
	}
	defer file.Close()

	// Write each pair of int and float64 to the file
	for i := range tasks {
		_, err := fmt.Fprintf(file, "%d, %.6f\n", tasks[i], seconds[i])
		if err != nil {
			fmt.Println("Error writing to file:", err)
			return
		}
	}
}
