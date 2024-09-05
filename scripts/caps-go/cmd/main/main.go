package main

import (
	"time"

	"casp.system.bu/placement/caps_multi"
)

func main() {

	// ///////////////////////// Example to call autotune /////////////////////////
	// // Init caps paras
	// parameterCAPS := &caps_multi.ParameterCAPS{
	// 	JobGraph_jsonFile:        "../../json/q8_16_512.json",
	// 	WorkerNum:                4,
	// 	SlotNum:                  16,
	// 	Outer_dfs_order:          "compute",
	// 	ThreadNum:                7,
	// 	SelectPlanAndWriteToFile: true,
	// 	IpList:                   []string{"192.168.1.8", "192.168.1.9", "192.168.1.12", "192.168.1.13"},
	// 	Config_file_name:         "schedulercfg",
	// 	TestCostCorrectness:      false,
	// }
	// // Init autotune paras
	// parameterAutoTune := &caps_multi.ParameterAutoTune{
	// 	// Search range
	// 	ComputeCeiling: 0.07,
	// 	StateCeiling:   0.07,
	// 	NetworkCeiling: 0.5,
	// 	// Search granularity
	// 	Granularity: 0.01,
	// 	// Relax rate
	// 	AutoTuneRate: 0.1,
	// 	// Timeout intervals
	// 	CeilingRelaxTimeout: 10 * time.Second,
	// 	Phase1Timeout:       10 * time.Second,
	// 	Phase2Timeout:       30 * time.Second,
	// }

	// // Call autotune
	// caps_multi.Auto_tuning(parameterCAPS, parameterAutoTune)

	/////////////////////// Example to call CAPS /////////////////////////
	// Init caps paras
	parameterCAPS := &caps_multi.ParameterCAPS{
		JobGraph_jsonFile: "../../json/mergedQuery.json",
		// JobGraph_jsonFile: "../../json/q8_16.json",
		// JobGraph_jsonFile: "../../json/q8_bench.json",
		Threshold_ratio: &caps_multi.ThresholdRatio{
			Compute: 0.08,
			State:   0.15,
			Network: 0.9,
		},
		WorkerNum:       20,
		SlotNum:         8,
		ExitOnFirstPlan: true,
		ExitOnTimeOut:   true,
		Outer_dfs_order: "compute",
		ThreadNum:       7,
		// Timeout interval if earlyExit is true
		Timeout: 500 * time.Millisecond,
		// Result processing parameters
		CalculateParetoPlans:     true,
		SelectPlanAndWriteToFile: true, // used when calculate pareto, if write plan to config file
		// IpList:                   []string{"192.168.1.8", "192.168.1.9", "192.168.1.12", "192.168.1.13"}, // used when WriteToFile is true
		IpList:              []string{"192.168.1.101", "192.168.1.102", "192.168.1.103", "192.168.1.104", "192.168.1.105", "192.168.1.106", "192.168.1.107", "192.168.1.108", "192.168.1.109", "192.168.1.110", "192.168.1.111", "192.168.1.112", "192.168.1.113", "192.168.1.114", "192.168.1.115", "192.168.1.116", "192.168.1.117", "192.168.1.118", "192.168.1.119", "192.168.1.120"},
		Config_file_name:    "schedulercfg", // used when WriteToFile is true
		TestCostCorrectness: false,
	}

	// // Call a single CAPS
	// caps_multi.RunCAPS(parameterCAPS)

	// Keep trying until a valid plan is found
	for {
		success := caps_multi.RunCAPS(parameterCAPS)
		if success {
			break
		}
	}

	// // Threading scalability test
	// res := []time.Duration{}
	// for i := 1; i <= 10; i++ {
	// 	parameterCAPS.ThreadNum = i
	// 	var sum time.Duration
	// 	for j := 0; j < 4; j++ {
	// 		startTime := time.Now()
	// 		caps_multi.RunCAPS(parameterCAPS)
	// 		endTime := time.Now()
	// 		sum += endTime.Sub(startTime)
	// 	}
	// 	res = append(res, sum/4)
	// }
	// fmt.Println(res)

}

// func run_single_caps() {
// 	jobGraph_jsonFile := "../../json/q8_16.json"
// 	threshold_ratio := &caps_single.ThresholdRatio{
// 		Compute: 0.0138,
// 		State:   0.0276,
// 		Network: 0.457188,
// 	}
// 	workerNum := 4
// 	slotNum := 16
// 	earlyExit := false
// 	outer_dfs_order := "default"

// 	caps_process_single := caps_single.NewCAPS(jobGraph_jsonFile, threshold_ratio, workerNum, slotNum, earlyExit, outer_dfs_order)
// 	caps_process_single.Start()
// }
