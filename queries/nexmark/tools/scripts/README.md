## scripts for compiling/running flink on cluster

before using, put this `script` folder under `flink-simplified` folder

### step0: configure

in this example we have 4 task managers, each task manager has 2 slots. -> 8 slots in total

0. setup all nodes. make sure the master node can `ssh` to all task managers without password (by adding ssh pub key to authorized keys)

1. change IP address of task managers in `workers`

2. change IP address of job manager in `masters` and `flink-conf.yaml`

3. change numberOfTaskSlots in `flink-conf.yaml` (num of slots per task manager)

4. If you wish to use custom scheduling, you need to finish the following steps:  (It is turned on now)

   4.1 Set `jobmanager.scheduler: Custom`

   4.2 Write the placement plan in `schedulercfg`. For each line, specify task name and the IP address of corresponding task manager. We have given an example for Nexmark Query1.

### step1: compile query

See [here](../../README.md)

We use Query1 in our demo.

### step2: compile flink

We tested under java 11 and Ubuntu 22.04

```
openjdk 11.0.15 2022-04-19
OpenJDK Runtime Environment (build 11.0.15+10-Ubuntu-0ubuntu0.22.04.1)
OpenJDK 64-Bit Server VM (build 11.0.15+10-Ubuntu-0ubuntu0.22.04.1, mixed mode, sharing)
```

`./makeflink.sh`

### step3: deploy flink on cluster

`./deployflink.sh`


### step4: stop flink on cluster

after finishing experiments,

`./stopflink.sh`


### Appendix

if you want to use `tc` for all nodes, use `./tcall.sh create` to limit bandwidth, and use `./tcall.sh` to cancel the limitation. 

Modify the ip address in `./tcall.sh` accordingly before using it.

