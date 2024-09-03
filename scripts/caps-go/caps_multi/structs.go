package caps_multi

import (
	"context"
	"sync"
	"time"
)

///////////////////////// Search Related Structs /////////////////////////

// Accumulated resource usage on a node
type Resource struct {
	Compute float64
	State   float64
	Network float64
}

// Logical operator in job graph
type Operator struct {
	// Unique id for the operator with byte type (range 0 to 255)
	// Assume # of logical operators in the job <= 255
	// This id is used as a partial key in the map to track current placements
	Id byte
	// Descriptive name of the operator
	Name string
	// Parallelism of the operator
	Parallelism int
	// List of downstream operators in logical graph
	DownNodes []byte
	// List of upstream operators in logical graph
	UpNodes []byte
	// The link type of the downstream ("FORWARD", "REBALANCE", "HASH")
	OutboundType string
	// Resource requirements
	ResRequirement *Resource
}

// Struct to track the placement decision during the search
type CurPlacement struct {
	// # of remaining available slots
	LeftSlots int
	// map tracking the current placement plan
	// Key: string indicates the task placement group on a node
	// Value: NodePlacementInfo
	Map map[string]*NodePlacementInfo
}

// Task placement info for a node: value for CurPlace map
type NodePlacementInfo struct {
	// Number of nodes with identical task placements
	Count int
	// Current accumulated resource usage on this node
	ResUsage *Resource
}

// Worker info for inner search process
type Node struct {
	// Initial task placement on this node
	Key string
	// Accumulated resource usage
	ResUsage *Resource
	// # tasks of the current OP to be deployed
	DeploymentCount int
}

// Temporary struct for calculating network cost
type OpCostTuple struct {
	Parallelism int
	ComputeCost float64
	StateCost   float64
	NetworkCost float64
}

// Plan found from the search
type Plan struct {
	// Task placement detail on each worker
	Placement []string
	// Cost of the plan (each dimension uses the bottleneck worker)
	Cost *Resource
}

//////////////////////////// Input Parameters ////////////////////////////

// Threshold parameter for dfs
type ThresholdRatio struct {
	Compute float64
	State   float64
	Network float64
}

// Parameters for start a CAPS process
type ParameterCAPS struct {
	// CAPS parameters
	JobGraph_jsonFile string
	Threshold_ratio   *ThresholdRatio
	WorkerNum         int
	SlotNum           int
	ExitOnFirstPlan   bool
	ExitOnTimeOut     bool
	Outer_dfs_order   string
	ThreadNum         int
	// Timeout interval if earlyExit is true
	Timeout time.Duration
	// Result processing parameters
	CalculateParetoPlans     bool
	SelectPlanAndWriteToFile bool     // used when calculate pareto, if write plan to config file
	IpList                   []string // used when WriteToFile is true
	Config_file_name         string   // used when WriteToFile is true
	TestCostCorrectness      bool     // do test on the cost value for all found plans
}

////////////////////////////// Thread Pool //////////////////////////////

type ThreadPool struct {
	// Number of routines in the thread pool
	ThreadNum int
	// List of tokens: each one indicates an available routine in the pool
	RoutineAllocator chan byte
	// Task queue for processing in parallel
	Scheduler chan *Task
	// Wait group for all tasks
	Task_wg *sync.WaitGroup
	// Wait group for all worker routines
	Worker_wg *sync.WaitGroup
	// Channel for merging the resulting plans
	PlanMerge chan *[]*Plan
	// Context on finding 1st plan
	CtxFirstPlan        context.Context
	CancelFuncFirstPlan context.CancelFunc
	// Context with timeout
	CtxTimeout        context.Context
	CancelFuncTimeout context.CancelFunc
}

type Task struct {
	// Pointer to a copied CAPS object (New created: DeployedOps, Ops, CurPlace, Plans)
	CAPS_copy *CAPS
	// Additional parameters required for InnerSearch
	Index        int
	Nodes        *[]*Node // Need deep copy
	LeftTasks    int
	LeftSlots    int
	Op           *Operator
	LastNodeType string
	BaseSlot     int
}

//////////////////////////// Struct Methods ////////////////////////////

// One has strictly higher cost than the other
func (res *Resource) IsDominatedBy(other_res *Resource) bool {
	// All dimensions have higher or equal cost than the other
	allLargerEqual := (res.Compute >= other_res.Compute && res.State >= other_res.State && res.Network >= other_res.Network)
	// At least 1 dimension has strictly higher cost than the other
	anyLarger := (res.Compute > other_res.Compute || res.State > other_res.State || res.Network > other_res.Network)
	return allLargerEqual && anyLarger
}
