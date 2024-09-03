package caps_multi

import (
	"fmt"
	"time"
)

type ParameterAutoTune struct {
	// Search ceilings for all dimensions
	ComputeCeiling float64
	StateCeiling   float64
	NetworkCeiling float64
	// Granularity for the search
	Granularity float64
	// Relax rate in phase 2
	AutoTuneRate float64
	// Relax ceiling timeout
	CeilingRelaxTimeout time.Duration
	// Phase 1 timeout
	Phase1Timeout time.Duration
	// Phase 2 timeout
	Phase2Timeout time.Duration
	// Number of CAPS repeat for 1) relax ceiling, 2) bineary search on each dimension
	NumRepeatSearch int
	// Number of CAPS repeat for finding final results
	NumRepeatResult int
}

// Autotune process
func Auto_tuning(parameterCAPS *ParameterCAPS, parameterAutoTune *ParameterAutoTune) {
	compute_c := parameterAutoTune.ComputeCeiling
	state_c := parameterAutoTune.StateCeiling
	network_c := parameterAutoTune.NetworkCeiling

	// Assign threshold to be all ceilings
	parameterCAPS.Threshold_ratio = &ThresholdRatio{
		Compute: compute_c,
		State:   state_c,
		Network: network_c,
	}
	parameterCAPS.ExitOnFirstPlan = true
	parameterCAPS.ExitOnTimeOut = true
	parameterCAPS.Timeout = parameterAutoTune.CeilingRelaxTimeout
	parameterCAPS.CalculateParetoPlans = false

	// Test if ceilings can find plans
	for {
		if tryCAPSRepeatly(parameterCAPS, parameterAutoTune.NumRepeatSearch) {
			break
		}
		fmt.Println("[Autotune Input Error] All ceilings cannot find a plan >>> relax ceilling")
		// Automatically relax the ceilling
		compute_c *= (1 + parameterAutoTune.AutoTuneRate)
		if compute_c > 1 {
			compute_c = 1
		}
		parameterCAPS.Threshold_ratio.Compute = compute_c

		state_c *= (1 + parameterAutoTune.AutoTuneRate)
		if state_c > 1 {
			state_c = 1
		}
		parameterCAPS.Threshold_ratio.State = state_c

		network_c *= (1 + parameterAutoTune.AutoTuneRate)
		if network_c > 1 {
			network_c = 1
		}
		parameterCAPS.Threshold_ratio.Network = network_c
	}
	fmt.Printf("[Autotune] new ceiling found >>> compute: %.6f, state: %.6f, network: %.6f\n", compute_c, state_c, network_c)

	// Start timer
	startTime := time.Now()

	// Phase 1: find minimum valid threshold for all dimensions
	// Reset timeout interval to phase 1 timeout
	parameterCAPS.Timeout = parameterAutoTune.Phase1Timeout

	// Compute
	min_valid_compute_ratio, ct_compute := binary_search(compute_c, parameterAutoTune.Granularity, parameterCAPS, &parameterCAPS.Threshold_ratio.Compute, "compute", parameterAutoTune.NumRepeatSearch)
	parameterCAPS.Threshold_ratio.Compute = compute_c

	// State
	min_valid_state_ratio, ct_state := binary_search(state_c, parameterAutoTune.Granularity, parameterCAPS, &parameterCAPS.Threshold_ratio.State, "state", parameterAutoTune.NumRepeatSearch)
	parameterCAPS.Threshold_ratio.State = state_c

	// Network
	min_valid_network_ratio, ct_network := binary_search(network_c, parameterAutoTune.Granularity, parameterCAPS, &parameterCAPS.Threshold_ratio.Network, "network", parameterAutoTune.NumRepeatSearch)

	// Phase 2: relax all ratio from min_valid until CAPS is success
	parameterCAPS.Threshold_ratio.Compute = min_valid_compute_ratio
	parameterCAPS.Threshold_ratio.State = min_valid_state_ratio
	parameterCAPS.Threshold_ratio.Network = min_valid_network_ratio
	parameterCAPS.ExitOnFirstPlan = false // Do not exit on 1st plan
	parameterCAPS.ExitOnTimeOut = true    // Exit if run too long
	parameterCAPS.Timeout = parameterAutoTune.Phase2Timeout
	parameterCAPS.CalculateParetoPlans = true

	ct_relax := 1
	for {
		fmt.Printf("[Autotune phase 2] trying ratio >>> compute: %.6f, state: %.6f, network: %.6f ... (iteration %d)\n", parameterCAPS.Threshold_ratio.Compute, parameterCAPS.Threshold_ratio.State, parameterCAPS.Threshold_ratio.Network, ct_relax)
		if tryCAPSRepeatly(parameterCAPS, parameterAutoTune.NumRepeatResult) {
			break
		}
		ct_relax += 1
		// Relax ratio
		parameterCAPS.Threshold_ratio.Compute *= (1 + parameterAutoTune.AutoTuneRate)
		if parameterCAPS.Threshold_ratio.Compute > 1 {
			parameterCAPS.Threshold_ratio.Compute = 1
		}
		parameterCAPS.Threshold_ratio.State *= (1 + parameterAutoTune.AutoTuneRate)
		if parameterCAPS.Threshold_ratio.State > 1 {
			parameterCAPS.Threshold_ratio.State = 1
		}
		parameterCAPS.Threshold_ratio.Network *= (1 + parameterAutoTune.AutoTuneRate)
		if parameterCAPS.Threshold_ratio.Network > 1 {
			parameterCAPS.Threshold_ratio.Network = 1
		}
	}

	// End timer
	endTime := time.Now()
	fmt.Println("[Autotune result] total runtime:", endTime.Sub(startTime))
	fmt.Println("[Autotune result] # CAPS calls | compute:", ct_compute, "| state:", ct_state, "| network:", ct_network, "| phase two:", ct_relax, "| total:", ct_compute+ct_state+ct_network+ct_relax)
	fmt.Printf("[Autotune result] final autotune ratio >>> compute: %.6f, state: %.6f, network: %.6f\n", parameterCAPS.Threshold_ratio.Compute, parameterCAPS.Threshold_ratio.State, parameterCAPS.Threshold_ratio.Network)
}

// Helper function for autotune phase 1
func binary_search(ceiling float64, min_diff float64, parameterCAPS *ParameterCAPS, target_dimension *float64, which string, numRepeat int) (float64, int) {
	low := float64(0)
	high := ceiling
	ct := 0
	for low < high {
		// Stop if (high - low) is smaller than the mininum granularity
		if high-low < min_diff {
			break
		}
		mid := low + (high-low)/2
		// Update threshold of the target dimension
		*target_dimension = mid
		// Print status
		fmt.Printf("[Autotune phase 1] trying %s cost minimum valid threshold ratio ... (%s iteration %d)\n", which, which, ct+1)

		// Try CAPS with ceiling on other dimensions
		if tryCAPSRepeatly(parameterCAPS, numRepeat) {
			high = mid
		} else {
			low = mid
		}
		ct += 1
	}
	return high, ct
}

// Try caps by repeating multiple times with small timeout interval
func tryCAPSRepeatly(parameterCAPS *ParameterCAPS, numRepeat int) bool {
	for i := 0; i < numRepeat; i++ {
		success := RunCAPS(parameterCAPS)
		if success {
			return true
		}
	}
	return false
}
