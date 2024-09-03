package main

import (
	"time"

	"casp.system.bu/placement/caps_multi"
)

func main() {

	///////////////////////// Example to call autotune /////////////////////////
	// Init caps paras
	parameterCAPS := &caps_multi.ParameterCAPS{
		// JobGraph_jsonFile: "../../json/singlequery/deem_16_512.json",
		// JobGraph_jsonFile:        "../../json/multiquery/multi_aligned.json",
		JobGraph_jsonFile: "../../json/singlequery_8slot/Q1_updated.json",
		// JobGraph_jsonFile: "../../json/singlequery_cloudlab/Q1_updated.json",
		// JobGraph_jsonFile:        "../../json/mergedQuery.json",
		WorkerNum:                4,
		SlotNum:                  8,
		Outer_dfs_order:          "compute",
		ThreadNum:                7,
		SelectPlanAndWriteToFile: true,
		// IpList:                   []string{"192.168.1.8", "192.168.1.9", "192.168.1.12", "192.168.1.13"},
		// IpList:              []string{"192.168.1.101", "192.168.1.102", "192.168.1.103", "192.168.1.104", "192.168.1.105", "192.168.1.106", "192.168.1.107", "192.168.1.108", "192.168.1.109", "192.168.1.110", "192.168.1.111", "192.168.1.112", "192.168.1.113", "192.168.1.114", "192.168.1.115", "192.168.1.116", "192.168.1.117"},
		// IpList: []string{"10.10.1.2", "10.10.1.3", "10.10.1.4", "10.10.1.5", "10.10.1.6"},
		// IpList: []string{"10.10.1.2", "10.10.1.3", "10.10.1.4"},
		IpList: []string{"192.168.1.101", "192.168.1.102", "192.168.1.103", "192.168.1.104"},
		// IpList:              []string{"10.10.1.2", "10.10.1.3"},
		Config_file_name:    "schedulercfg",
		TestCostCorrectness: false,
	}
	// Init autotune paras
	parameterAutoTune := &caps_multi.ParameterAutoTune{
		// Search range
		ComputeCeiling: 0.02,
		StateCeiling:   0.02,
		// StateCeiling:   0.05,
		NetworkCeiling: 0.1,
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

	// Call autotune
	caps_multi.Auto_tuning(parameterCAPS, parameterAutoTune)

}
