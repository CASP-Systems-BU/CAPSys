package caps_single

import (
	"fmt"
	"os"
	"time"
)

// CAPS struct
type CAPS struct {
	// If this run is to find bound
	EarlyExit bool
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
}

// Initialize CAPS
func NewCAPS(jobGraph_jsonFile string, threshold_ratio *ThresholdRatio, workerNum int, slotNum int, earlyExit bool, outer_dfs_order string) *CAPS {
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

	// Calculate thresholds for different dimensions
	threshold_compute, threshold_state, threshold_network := CalculateThreshold(ops, workerNum, slotNum, threshold_ratio)

	return &CAPS{
		EarlyExit:   earlyExit,
		DeployedOps: make(map[byte]bool),
		Ops:         ops,
		OpsMap:      opsMap,
		WorkerNum:   workerNum,
		SlotNum:     slotNum,
		CurPlace:    curPlace,
		Plans:       &plans,
		Threshold: &Resource{
			Compute: threshold_compute,
			Network: threshold_network,
			State:   threshold_state,
		},
	}
}

// Outer search
func (caps *CAPS) OuterSearch() {
	// Successfully placed all tasks
	if len(*caps.Ops) == 0 {
		// Copy the plan and add it to the Plans
		plan := caps.GeneratePlan()
		*(caps.Plans) = append(*(caps.Plans), plan)
		if caps.EarlyExit {
			// TODO: immediately stop the search
			os.Exit(1)
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
		caps.InnerSearch(index+1, nodes, leftTasks-num, leftSlots-slots, op, (*nodes)[index].Key, num)
		// Backtrace nodes
		caps.BacktraceNode((*nodes)[index], op, num, addedlocalnwcost)
	}
}

// Start the search
func (caps *CAPS) Start() {

	// Start from outer search
	startTime := time.Now()
	caps.OuterSearch()
	endTime := time.Now()
	searchTime := endTime.Sub(startTime)

	// [Test] Test the cost value for all plans
	caps.TestCostCorrectnessForAllPlans()

	// // Get pareto-optimal plans
	startTime = time.Now()
	pareto_plans := caps.ParetoOptimalPlans()
	endTime = time.Now()
	paretoTime := endTime.Sub(startTime)

	// Select a random plan from pareto-optimal set
	// TODO

	// Print status
	fmt.Println("Total plans:", len(*caps.Plans))
	fmt.Println("Pareto-optimal plans:", len(pareto_plans))
	fmt.Println("Search time:", searchTime)
	fmt.Println("Pareto-optimal time:", paretoTime)

	// // [Test] Print out pareto plans
	// for _, plan := range pareto_plans {
	// 	// caps.PrintOutPlan(plan)
	// 	caps.PrintOutPlanCost(plan)
	// }
}
