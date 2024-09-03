package caps_multi

import (
	"fmt"
	"time"
)

// CAPS struct
type CAPS struct {
	// Exit the search upon 1st found plan
	ExitOnFirstPlan bool
	// Exit the search upon timeout
	ExitOnTimeOut bool
	// Hash set recording the deployed OPs
	DeployedOps map[byte]bool
	// Streaming job: Operator stack used for the outer search process
	Ops *[]*Operator
	// Reference map
	OpsMap map[byte]*Operator
	// # of workers in the cluster
	WorkerNum int
	// # of slots per worker
	SlotNum int
	// Structure to track the placement along the search
	CurPlace *CurPlacement
	// Structure to store all found plans
	Plans *[]*Plan
	// Threshold value for 3 dimensions
	Threshold *Resource
	// Thread pool info
	Routines *ThreadPool
}

// Initialize CAPS
func NewCAPS(jobGraph_jsonFile string, threshold_ratio *ThresholdRatio, workerNum int, slotNum int, threadNum int, exitOnFirstPlan bool, exitOnTimeOut bool, outer_dfs_order string, timeout time.Duration) *CAPS {
	// Check if the threshold ratio is valid
	CheckThresholdRatio(threshold_ratio)

	// Read job graph and construct the operator stack
	ops := ReadJsonJG(jobGraph_jsonFile)

	// Check if the compute graph is valid
	CheckOPs(ops, workerNum, slotNum)

	// Sort the ops based on outer_dfs_order
	ops = SortOuterSearch(ops, outer_dfs_order)

	// Init the reference map
	opsMap := InitOpsReferenceMap(ops)

	// Initialize the CurPlacement structure
	curPlace := NewCurPlacement(workerNum, slotNum)

	// Initialize the resulting placement plans
	plans := []*Plan{}

	// Initialize the ThreadPool
	routines := NewThreadPool(threadNum, timeout)

	// Calculate thresholds for different dimensions
	threshold_compute, threshold_state, threshold_network := CalculateThreshold(ops, workerNum, slotNum, threshold_ratio)

	return &CAPS{
		ExitOnFirstPlan: exitOnFirstPlan,
		ExitOnTimeOut:   exitOnTimeOut,
		DeployedOps:     make(map[byte]bool),
		Ops:             ops,
		OpsMap:          opsMap,
		WorkerNum:       workerNum,
		SlotNum:         slotNum,
		CurPlace:        curPlace,
		Plans:           &plans,
		Threshold: &Resource{
			Compute: threshold_compute,
			Network: threshold_network,
			State:   threshold_state,
		},
		Routines: routines,
	}
}

// Invoke a CAPS process and return true if successfully find plan
func RunCAPS(para *ParameterCAPS) bool {
	// CAPS parameters
	jobGraph_jsonFile := para.JobGraph_jsonFile
	threshold_ratio := para.Threshold_ratio
	workerNum := para.WorkerNum
	slotNum := para.SlotNum
	exitOnFirstPlan := para.ExitOnFirstPlan
	exitOnTimeOut := para.ExitOnTimeOut
	outer_dfs_order := para.Outer_dfs_order
	threadNum := para.ThreadNum
	// Timeout interval if earlyExit is true
	timeout := para.Timeout
	// Result processing parameters
	calculateParetoPlans := para.CalculateParetoPlans
	selectPlanAndWriteToFile := para.SelectPlanAndWriteToFile
	ipList := para.IpList
	config_file_name := para.Config_file_name
	testCostCorrectness := para.TestCostCorrectness

	// Find all satisfactory plans
	startTime := time.Now()
	caps := NewCAPS(jobGraph_jsonFile, threshold_ratio, workerNum, slotNum, threadNum, exitOnFirstPlan, exitOnTimeOut, outer_dfs_order, timeout)
	exitCode := caps.Start()
	endTime := time.Now()
	fmt.Println("[CAPS Result] CAPS time:", endTime.Sub(startTime))
	fmt.Println("[CAPS Result] Total # plans:", len(*caps.Plans))
	// Terminated on timeout
	if exitCode == 2 {
		fmt.Println("[CAPS Result] 			Timeout!")
	}

	// Get pareto-optimal plans
	if calculateParetoPlans && len(*caps.Plans) > 0 {
		// If total # plans is too large >>> limit it to 10k plans
		if len(*caps.Plans) > 10000 {
			*caps.Plans = (*caps.Plans)[:10000]
			fmt.Println("[CAPS Result] # plans too many >>> reduce it to 10k to calculate pareto plans", len(*caps.Plans))
		}

		startTime = time.Now()
		pareto_plans := caps.ParetoOptimalPlans()
		endTime = time.Now()
		paretoTime := endTime.Sub(startTime)
		fmt.Println("[CAPS Result] Pareto-optimal time:", paretoTime)
		fmt.Println("[CAPS Result] Pareto-optimal plans:", len(pareto_plans))

		// Write a random pareto-optimal plan to file
		if selectPlanAndWriteToFile {
			caps.GeneratePlacementConfigFile(ipList, config_file_name, pareto_plans)
		}
	}

	// [Test] Test the cost value for all plans
	if testCostCorrectness {
		caps.TestCostCorrectnessForAllPlans()
	}

	// Return success if at least a plan is found
	if len(*caps.Plans) > 0 {
		return true
	} else {
		return false
	}
}

// Outer search
func (caps *CAPS) OuterSearch() {
	// Successfully placed all tasks
	if len(*caps.Ops) == 0 {
		// Copy the plan and add it to the Plans
		plan := caps.GeneratePlan()
		*(caps.Plans) = append(*(caps.Plans), plan)
		if caps.ExitOnFirstPlan {
			// Immediately stop the search and notify all worker routines
			fmt.Println("[Early exit] Found a plan and close all routines")
			caps.Routines.CancelFuncFirstPlan()
		}
		return
	}
	// Continue explore the next operator
	op := caps.Pop_from_Ops()
	nodes := caps.BuildNodeList()
	// Call inner search
	caps.InnerSearch(0, nodes, op.Parallelism, caps.CurPlace.LeftSlots, op, "initial_invalid", -1)
	caps.Push_to_Ops(op)
}

// Inner search
func (caps *CAPS) InnerSearch(index int, nodes *[]*Node, leftTasks int, leftSlots int, op *Operator, lastNodeType string, baseSlot int) {
	// Check if 1st plan has been found if ExitOnFirstPlan
	if caps.ExitOnFirstPlan {
		select {
		case <-caps.Routines.CtxFirstPlan.Done():
			return
		default:
		}
	}
	// Check if timeout if ExitOnTimeOut
	if caps.ExitOnTimeOut {
		select {
		case <-caps.Routines.CtxTimeout.Done():
			return
		default:
		}
	}

	// All tasks of this OP are placed
	if leftTasks == 0 {
		// A corner case to prune duplicate branch
		if index < len(*nodes) && (*nodes)[index].Key == lastNodeType {
			return
		}
		// Check if the upstream ops are already placed
		deployedUpNodeList := []byte{}
		for _, upOp := range op.UpNodes {
			if _, ok := caps.DeployedOps[upOp]; ok {
				deployedUpNodeList = append(deployedUpNodeList, upOp)
			}
		}
		// If there are upstream ops deployed!
		localnwcosts := make([]float64, len(*nodes))
		if len(deployedUpNodeList) != 0 {
			for i, node := range *nodes {
				localnwcost := float64(0)
				numDownOpDeployed := node.DeploymentCount
				downOpPara := op.Parallelism
				// Check each upstream operator on this node
				for _, upOp := range deployedUpNodeList {
					upOpnwcost := caps.OpsMap[upOp].ResRequirement.Network
					numUpOpDeployed := 0
					for _, task := range ConvertTaskStrToArray(node.Key) {
						if task == upOp {
							numUpOpDeployed += 1
						}
					}
					if caps.OpsMap[upOp].OutboundType == "FORWARD" {
						remote_link_count := numUpOpDeployed - numDownOpDeployed
						if remote_link_count < 0 {
							remote_link_count = 0
						}
						localnwcost += upOpnwcost * float64(remote_link_count)
					} else {
						localnwcost += (float64(1) - float64(numDownOpDeployed)/float64(downOpPara)) * upOpnwcost * float64(numUpOpDeployed)
					}
				}
				// Check localnwcost and prune the branch if necessary
				if (node.ResUsage.Network + localnwcost) > caps.Threshold.Network {
					return
				}
				localnwcosts[i] = localnwcost
			}
			// Now apply the network cost update to nodes
			for i, node := range *nodes {
				node.ResUsage.Network += localnwcosts[i]
			}
		}
		// Update CurPlace for next OP
		oldCurPlace := caps.UpdateCurPlace(nodes, op)
		caps.DeployedOps[op.Id] = true
		// Explore next OP
		caps.OuterSearch()
		// Backtrace
		caps.BacktraceCurPlace(oldCurPlace)
		delete(caps.DeployedOps, op.Id)
		// Now backtrace nodes if upstream nwcost is updated above
		for i, node := range *nodes {
			node.ResUsage.Network -= localnwcosts[i]
		}
		return
	}
	// Now keep exploring the next node to deploy tasks of the current OP
	slots := caps.SlotNum - len((*nodes)[index].Key)
	atMost := leftTasks
	if slots < leftTasks {
		atMost = slots
	}
	diff := leftTasks - (leftSlots - slots)
	atLeast := diff
	if diff < 0 {
		atLeast = 0
	}
	// Check duplicate node and remove duplicate branches
	if (*nodes)[index].Key == lastNodeType {
		if atMost < baseSlot {
			return
		}
		if baseSlot > atLeast {
			atLeast = baseSlot
		}
	}
	// Now explore all possible placement at this node
	for num := atLeast; num <= atMost; num++ {
		// Update this node in nodes
		addedlocalnwcost := caps.UpdateNode((*nodes)[index], op, num)

		// Branch pruning on a local node placement of current OP:
		// (1) Cost Filter: compute (expected busy time)
		if (*nodes)[index].ResUsage.Compute > caps.Threshold.Compute {
			caps.BacktraceNode((*nodes)[index], op, num, addedlocalnwcost)
			break
		}

		// (2) Cost Filter: I/O (iowrite + ioread)
		if (*nodes)[index].ResUsage.State > caps.Threshold.State {
			caps.BacktraceNode((*nodes)[index], op, num, addedlocalnwcost)
			break
		}

		// (3) Cost Filter: network (ourbound traffic)
		if (*nodes)[index].ResUsage.Network > caps.Threshold.Network {
			caps.BacktraceNode((*nodes)[index], op, num, addedlocalnwcost)
			break
		}

		// Continue to explore next node
		routines := caps.Routines
		select {
		// Try to split the search to another worker
		case <-routines.RoutineAllocator:
			// Successfully reserve the routine, prepare the new task sent to the new routine
			caps_copy, nodes_copy := caps.DeepCopyForTask(nodes)
			// Init the task
			task := &Task{
				CAPS_copy:    caps_copy,
				Index:        index + 1,
				Nodes:        nodes_copy,
				LeftTasks:    leftTasks - num,
				LeftSlots:    leftSlots - slots,
				Op:           op,
				LastNodeType: (*nodes)[index].Key,
				BaseSlot:     num,
			}
			// Send the new task to the scheduler
			routines.Task_wg.Add(1)
			routines.Scheduler <- task
		// No free routine available, continue processing locally
		default:
			caps.InnerSearch(index+1, nodes, leftTasks-num, leftSlots-slots, op, (*nodes)[index].Key, num)

		}
		// Backtrace nodes
		caps.BacktraceNode((*nodes)[index], op, num, addedlocalnwcost)
	}
}

// Start the search
func (caps *CAPS) Start() int {

	// Start all worker routines
	caps.StartThreadingPool()

	// Start the routine for merging plans obtained from all worker routines
	plans := caps.StartPlanMergeThread()

	// Allocate a routine and schedule the 1st task
	routines := caps.Routines
	<-routines.RoutineAllocator
	routines.Task_wg.Add(1)
	routines.Scheduler <- &Task{
		Index: -1,
	}

	// Gracefully terminate all routines
	exitCode := caps.GracefulTerminate()

	// Merge plans found from all routines into a single slice []*Plan
	caps.MergePlansToSingleSlice(plans)

	return exitCode
}
