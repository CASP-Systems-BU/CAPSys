# CAPSys

Welcome to the CAPSys repository!
This repository contains instructions for reproducing the experiments in [our EuroSys'25 paper "CAPSys: Contention-aware task placement for data stream processing"](https://hdl.handle.net/2144/49285).

CAPSys is an adaptive resource controller for dataflow stream processors, that considers auto-scaling and task placement in concert. CAPSys relies on Contention-Aware Placement Search (CAPS), a new placement strategy that ensures compute-intensive, I/O-intensive, and network-intensive tasks are balanced across available resources. We integrate CAPSys with Apache Flink and show that it consistently achieves higher throughput and lower backpressure than Flink's strategies, while it also improves the convergence of the DS2 auto-scaling controller under variable workloads. When compared with the state-of-the-art ODRP placement strategy, CAPSys computes the task placement in orders of magnitude lower time and achieves up to 6X higher throughput. The experiments require both AWS and Cloudlab resources to support the above claims.


### Please check [here](https://github.com/CASP-Systems-BU/CAPSys/tree/main/scripts#readme) for detailed instructions.
