'''
run job with dynamic rate + without state/savepoint

2. Starting from a good initial placement (can meet the target rate and is not over-provisioned and we can show that with busy time and idle time), we  vary the input rate every $10min$ and trigger a DS2 scaling action at each interval. We set the initial target rate to \vasia{X} and we first increase it for three intervals and then decrease it for another three. We measure throughput, latency, backpressure, and resources assigned. % for each interval

start job with apply placement in "schedulercfg1st" in json
for iterations:
    profile+collect metric for $RUNPERD sec
    apply DS2
    restart with new parallelism+placement
'''

# python3 rundynamic2.py expjson/deem_dynamic8x2.json costpath start custom_1

from dfs import *
from exputils import *
import copy

def custom_formatter(x):
    return f"{x:.2f}"

np.set_printoptions(threshold=np.inf, linewidth=np.inf, edgeitems=10)
np.set_printoptions(formatter={'all': custom_formatter})


# output config file name
config_file_name = 'schedulercfg'

# wait some time to warm up
WARMUP=170
# activation time: period(sec) of each iteration
RUNPERD=180
# policy interval: frequency of profiling (every $RUNFREQ seconds) in each period
RUNFREQ=5
# num of iterations
NUMITER=5

TARGET_RATE_RATIO=0.95
TARGET_UTIL=0.7

#------------------------------------# get cmd argument
fjson=sys.argv[1]
COSTPATH=sys.argv[2]
tcmd=sys.argv[3]
RUNID=sys.argv[4]

_DEBUG=""
if(len(sys.argv)>4):
    _DEBUG=sys.argv[4]


# for dynamic rate query, need savepoint to save current rate
fromsavepoint=True

#------------------------------------# read json and get job configuration
cfg=json.loads(open(fjson,'r').read())
jarpath=cfg['jarpath']
jarargs=cfg['jarargs']
expname=cfg['expname']
iplist=cfg['iplist']
workers_ip=[ip for ip in cfg['iplist']]
jmip=cfg['jmip']
kafkaip=cfg['kafkaip']
KAFKAROOT=cfg['KAFKAROOT']
iolimit=cfg['iolimit']
tclimit=cfg['tclimit']
tcnic=cfg['tcnic']
user=cfg['user']
jmpt=cfg['jmpt']
FLINKROOT=cfg['FLINKROOT']
TMPROOT=cfg['TMPROOT']
SAVEROOT=cfg['SAVEROOT']
ctype=cfg['ctype']
resetsec=cfg['resetsec']
srcratelist=cfg['srcratelist']    # target_input_rate
oprlist=cfg['oprlist']    # flink job parameters that tunes parallelism
mapping=cfg['mapping']    # mapping of operator name from flink_metrics to schedulercfg
schedulercfg1st=cfg['schedulercfg1st']
# num of slots per worker
workers_slot=cfg['workers_slot']

DEPLOYTIME=0    # deploy time since last recfg
PASTDURATION=0    # running duration befor last recfg

# Configurable parameters to tune the dfs threshold
planNum = cfg['dfs']['planNum']
step_ratio_compute = cfg['dfs']['step_ratio_compute']
step_ratio_io = cfg['dfs']['step_ratio_io']
step_ratio_network = cfg['dfs']['step_ratio_network']
randomOptimal = cfg['dfs']['randomOptimal']
paras = MicrobenchmarkParas(planNum, step_ratio_compute, step_ratio_io, step_ratio_network)


def getCurrentTops():
    global PASTDURATION
    global DEPLOYTIME
    duration=PASTDURATION + (int(time.time())-DEPLOYTIME)
    rl=srcratelist[0]["Source"].split("_")
    for i in range(0,len(rl),2):
        _rate = int(rl[i])
        _dur  = int(rl[i+1])
        duration -= _dur
        if(duration<=0):
            return(_rate)
    return(-1)    # job already finished


def getMetricsWarmup(WARMUP, _JobGraph, _runiter, vertex_ids, job_id):
    workerCpuUtils = {}
    for ip in workers_ip:
        workerCpuUtils[ip] = []

    JobGraph=copy.deepcopy(_JobGraph)
    toposeq=list(nx.topological_sort(JobGraph))    # topological_sort on operators
    print("topological_sort:    ", toposeq)
    _period=WARMUP
    #------------------------------------# run a period
    while(_period>0):
        time.sleep(RUNFREQ)
        _period-=RUNFREQ
        print("        ITERATION:", str(_runiter), "WARMUP:", str(_period), "-------")

        #------------------------------------# get cpu utilization metrics for each worker

        # pull cpu util metrics for each worker during experiment phase
        for key, value in workerCpuUtils.items():
            value.append(int(str2float(get_prometheus_cpuutil(jmip, key))*10))
            workerCpuUtils[key] = value

        JobGraphDict=defaultdict(nested_dict)
        for vid in JobGraph.nodes:
            JobGraphDict[vid]['_cpuutil']=np.array([])
            JobGraphDict[vid]['_oip']=np.array([])
            JobGraphDict[vid]['_oop']=np.array([])
            JobGraphDict[vid]['_tip']=np.array([])
            JobGraphDict[vid]['_top']=np.array([])
            JobGraphDict[vid]['_idletime']=np.array([])
            JobGraphDict[vid]['_bkpstime']=np.array([])
            JobGraphDict[vid]['_busytime']=np.array([])
            JobGraphDict[vid]['_ioread']=np.array([])
            JobGraphDict[vid]['_iowrite']=np.array([])
            JobGraphDict[vid]['_oib']=np.array([])
            JobGraphDict[vid]['_oob']=np.array([])
            JobGraphDict[vid]['parallelism']=JobGraph.nodes[vid]['parallelism']
            JobGraphDict[vid]['name']=JobGraph.nodes[vid]['name']

        #------------------------------------# Get profiling data per subtask
        for vid in vertex_ids:    # vid: operator id
            vertix=get_task_vertix_details(jmip, jmpt, job_id, vid)
            #vts=str(vertix['now'])
            _vname=vertix['name']
            vname=_vname.replace(' ','_').replace(',','_').replace(';','_')        # operator name
            #vpall=str(vertix['parallelism'])
            for vtask in vertix['subtasks']:
                ttm=vtask['taskmanager-id']    # taskmanager id of current subtask.  "192.168.1.12:39287-373453"
                tmip=ttm.split(":")[0]
                tid=str(vtask['subtask'])    # subtask id
                # only pull cpu usage for task during profile phase
                st_cpuutil = int(str2float(get_prometheus_cpuutil(jmip, tmip))*10)
                st_busytime = str2int(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.busyTimeMsPerSecond')[0]['value'])
                st_bkpstime = str2int(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.backPressuredTimeMsPerSecond')[0]['value'])
                st_idletime = str2int(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.idleTimeMsPerSecond')[0]['value'])
                st_oip = str2int(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.numRecordsInPerSecond')[0]['value'])
                st_oop = str2int(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.numRecordsOutPerSecond')[0]['value'])
                st_ioread = str2int(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.'+_vname+'.rocksdb_bytes_read')[0]['value'])
                st_iowrite = str2int(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.'+_vname+'.rocksdb_bytes_written')[0]['value'])
                st_oib = str2int(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.numBytesInPerSecond')[0]['value'])
                st_oob = str2int(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.numBytesOutPerSecond')[0]['value'])
                if st_busytime==0:
                    st_busytime=1    # avoid divide 0 error
                st_tip = st_oip / (st_busytime/1000)
                st_top = st_oop / (st_busytime/1000)
                if _DEBUG=="d":
                    print("metric per task:  ", vid,'--------'+vname+'_'+tid+"\n", "busytime", st_busytime, "bkpstime", st_bkpstime, "idletime", st_idletime, "oip", st_oip, "oop", st_oop, "tip", st_tip, "top", st_top)
                JobGraphDict[vid]['_cpuutil']=np.append(JobGraphDict[vid]['_cpuutil'], st_cpuutil)
                JobGraphDict[vid]['_oip']=np.append(JobGraphDict[vid]['_oip'], st_oip)
                JobGraphDict[vid]['_oop']=np.append(JobGraphDict[vid]['_oop'], st_oop)
                JobGraphDict[vid]['_idletime']=np.append(JobGraphDict[vid]['_idletime'], st_idletime)
                JobGraphDict[vid]['_bkpstime']=np.append(JobGraphDict[vid]['_bkpstime'], st_bkpstime)
                JobGraphDict[vid]['_busytime']=np.append(JobGraphDict[vid]['_busytime'], st_busytime)
                JobGraphDict[vid]['_ioread']=np.append(JobGraphDict[vid]['_ioread'], st_ioread)
                JobGraphDict[vid]['_iowrite']=np.append(JobGraphDict[vid]['_iowrite'], st_iowrite)
                JobGraphDict[vid]['_oib']=np.append(JobGraphDict[vid]['_oib'], st_oib)
                JobGraphDict[vid]['_oob']=np.append(JobGraphDict[vid]['_oob'], st_oob)
                JobGraphDict[vid]['_tip']=np.append(JobGraphDict[vid]['_tip'], st_tip)
                JobGraphDict[vid]['_top']=np.append(JobGraphDict[vid]['_top'], st_top)

        #------------------------------------# Calc optimal parallelism with ds2
        for vid in toposeq:    # calc true input/output rate
            parallelism=JobGraphDict[vid]['parallelism']
            JobGraphDict[vid]['cpuutil']=np.mean(JobGraphDict[vid]['_cpuutil'])
            JobGraphDict[vid]['idletime']=np.mean(JobGraphDict[vid]['_idletime'])    # average of all tasks of an operator
            JobGraphDict[vid]['bkpstime']=np.mean(JobGraphDict[vid]['_bkpstime'])
            JobGraphDict[vid]['busytime']=np.mean(JobGraphDict[vid]['_busytime'])
            JobGraphDict[vid]['oip']=np.sum(JobGraphDict[vid]['_oip'])    # sum of all tasks of an operator
            JobGraphDict[vid]['oop']=np.sum(JobGraphDict[vid]['_oop'])
            JobGraphDict[vid]['oib']=np.sum(JobGraphDict[vid]['_oib'])
            JobGraphDict[vid]['oob']=np.sum(JobGraphDict[vid]['_oob'])
            JobGraphDict[vid]['tip']=np.sum(JobGraphDict[vid]['_tip'])
            JobGraphDict[vid]['top']=np.sum(JobGraphDict[vid]['_top'])
            JobGraphDict[vid]['ioread']=np.sum(JobGraphDict[vid]['_ioread'])
            JobGraphDict[vid]['iowrite']=np.sum(JobGraphDict[vid]['_iowrite'])
            if JobGraphDict[vid]['busytime']<0:    # for source operators, busytime == NaN, true_rate == target_input_rate * source_parallelism
                JobGraphDict[vid]['tip']=0
                JobGraphDict[vid]['top']=getCurrentTops()*parallelism    # target_input_rate = src[srcname]*parallelism
                JobGraphDict[vid]['tops']=JobGraphDict[vid]['top']
            if(JobGraphDict[vid]['oip']>0):
                JobGraphDict[vid]['selectivity']=JobGraphDict[vid]['oop']/JobGraphDict[vid]['oip']
            if JobGraphDict[vid]['tip'] == 0:
                JobGraphDict[vid]['tip'] = 1
        for vid in toposeq:    # calc optimal parallelism for current interval
            parallelism=JobGraphDict[vid]['parallelism']
            selectivity=JobGraphDict[vid]['selectivity']
            innodes=JobGraph.nodes[vid]['innodes']
            if(len(innodes)==0):    # source
                JobGraphDict[vid]['optimalparallelism']=parallelism
            else:
                utops=0    # aggregated target output of its all upstream operator
                for uid in innodes:
                    utops+=JobGraphDict[uid]['tops']
                JobGraphDict[vid]['tips']=utops    # target input rate of current operator
                JobGraphDict[vid]['tops']=utops*selectivity    # target output rate of current operator
                #JobGraphDict[vid]['optimalparallelism']=math.ceil((utops/(JobGraphDict[vid]['tip']*TARGET_UTIL))*parallelism)
            JobGraph.nodes[vid]['_cpuutil']=np.append(JobGraph.nodes[vid]['_cpuutil'], JobGraphDict[vid]['cpuutil'])
            JobGraph.nodes[vid]['_tops']=np.append(JobGraph.nodes[vid]['_tops'], JobGraphDict[vid]['tops'])
            JobGraph.nodes[vid]['_tips']=np.append(JobGraph.nodes[vid]['_tips'], JobGraphDict[vid]['tips'])
            JobGraph.nodes[vid]['_top']=np.append(JobGraph.nodes[vid]['_top'], JobGraphDict[vid]['top'])
            JobGraph.nodes[vid]['_tip']=np.append(JobGraph.nodes[vid]['_tip'], JobGraphDict[vid]['tip'])
            JobGraph.nodes[vid]['_oop']=np.append(JobGraph.nodes[vid]['_oop'], JobGraphDict[vid]['oop'])
            JobGraph.nodes[vid]['_oip']=np.append(JobGraph.nodes[vid]['_oip'], JobGraphDict[vid]['oip'])
            JobGraph.nodes[vid]['_idletime']=np.append(JobGraph.nodes[vid]['_idletime'], JobGraphDict[vid]['idletime'])
            JobGraph.nodes[vid]['_bkpstime']=np.append(JobGraph.nodes[vid]['_bkpstime'], JobGraphDict[vid]['bkpstime'])
            JobGraph.nodes[vid]['_busytime']=np.append(JobGraph.nodes[vid]['_busytime'], JobGraphDict[vid]['busytime'])
            JobGraph.nodes[vid]['_ioread']=np.append(JobGraph.nodes[vid]['_ioread'], JobGraphDict[vid]['ioread'])
            JobGraph.nodes[vid]['_iowrite']=np.append(JobGraph.nodes[vid]['_iowrite'], JobGraphDict[vid]['iowrite'])
            JobGraph.nodes[vid]['_selectivity']=np.append(JobGraph.nodes[vid]['_selectivity'], JobGraphDict[vid]['selectivity'])
            JobGraph.nodes[vid]['_oob']=np.append(JobGraph.nodes[vid]['_oob'], JobGraphDict[vid]['oob'])
            JobGraph.nodes[vid]['_oib']=np.append(JobGraph.nodes[vid]['_oib'], JobGraphDict[vid]['oib'])
            #JobGraph.nodes[vid]['_optimalparallelism']=np.append(JobGraph.nodes[vid]['_optimalparallelism'], JobGraphDict[vid]['optimalparallelism'])
            JobGraph.nodes[vid]['_timestamp']=np.append(JobGraph.nodes[vid]['_timestamp'], time.time())
            # _pertaskdict = pd.DataFrame()
            _pertaskdict = {}
            _pertaskdict['_cpuutil'] = JobGraphDict[vid]['_cpuutil']
            _pertaskdict['_top'] = JobGraphDict[vid]['_top']
            _pertaskdict['_tip'] = JobGraphDict[vid]['_tip']
            _pertaskdict['_oop'] = JobGraphDict[vid]['_oop']
            _pertaskdict['_oip'] = JobGraphDict[vid]['_oip']
            _pertaskdict['_oob'] = JobGraphDict[vid]['_oob']
            _pertaskdict['_oib'] = JobGraphDict[vid]['_oib']
            _pertaskdict['_bkpstime'] = JobGraphDict[vid]['_bkpstime']
            _pertaskdict['_busytime'] = JobGraphDict[vid]['_busytime']
            _pertaskdict['_idletime'] = JobGraphDict[vid]['_idletime']
            JobGraph.nodes[vid]['_pertask'].append([_pertaskdict])

    pickle.dump(JobGraph, open(RUNPATH+"/"+str(_runiter)+"_warmup_jg.pkl", "wb"))
    pickle.dump(workerCpuUtils, open(RUNPATH+"/"+str(_runiter)+"_warmup_cpuutil.pkl", "wb"))


def rundynamic(_runiter):
    print("running iteration "+str(_runiter)+" --------------------------------------")
    run1_top = getCurrentTops()

    global workers_ip
    global PASTDURATION
    global DEPLOYTIME
    # initiate a map of workers: pull cpu util metrics
    workerCpuUtils = {}
    for ip in workers_ip:
        workerCpuUtils[ip] = []

    #------------------------------------# get job info
    rest_client = FlinkRestClient.get(host=jmip, port=jmpt)
    rest_client.overview()
    job_id = getRunningJobID(jmip, jmpt)
    vertex_ids=rest_client.jobs.get_vertex_ids(job_id)
    job = rest_client.jobs.get(job_id=job_id)

    tmidlist=[]
    for tm in rest_client.taskmanagers.all():
        tmidlist.append(tm['id'])

    #------------------------------------# generate logical dataflow
    print("starting......  job_id:", job_id)
    job_plan=get_job_plan_details(jmip, jmpt, job_id)['plan']['nodes']
    print("job_plan:  ", job_plan)
    JobGraph=nx.DiGraph()
    for opr in job_plan:
        oname=opr['description'].replace(' ','_').replace('+','_').replace('-','_').replace(',','_').replace(':','_').replace(';','_').replace('<br/>','').replace('(','_').replace(')','_')
        innodes=[x['id'] for x in opr['inputs']] if ('inputs' in opr) else []
        JobGraph.add_node(opr['id'], parallelism=opr['parallelism'], name=oname, pname=oname,    # vid, parallelism, name of current operator, name to be printed in schedulercfg
                          innodes=innodes,    # vid of upstream operators
                          outboundtype="",    # outbound link type (REBALANCE/HASH/FORWARD)
                          _ttm=np.array([]), _cpuutil=np.array([]), cpuutil=0,
                          _oip=np.array([]), _oop=np.array([]), _tip=np.array([]), _top=np.array([]), _tops=np.array([]), _tips=np.array([]),
                          _busytime=np.array([]), _bkpstime=np.array([]), _idletime=np.array([]), _selectivity=np.array([]),
                          _optimalparallelism=np.array([]), _ioread=np.array([]), _iowrite=np.array([]), _oib=np.array([]), _oob=np.array([]),
                          _pertask=[], _timestamp=np.array([]),
                          oip=0, oop=0,    # aggregated observed input/output records rate among all subtasks
                          tip=0, top=0,    # aggregated true input/output records rate among all subtasks
                          tops=0, tips=0,
                          busytime=0, bkpstime=0, idletime=0, selectivity=0.0,    # average of metric among all subtasks
                          optimalparallelism=0,
                          maxoptimalparallelism=0,
                          ioread=0, iowrite=0,    # aggregated rocksdb IO bytes rate among all subtasks
                          cpcost=0, nwcost=0, iocost=0,    # compute / network cost
                          oib=0, oob=0    # aggregated observed input/output bytes rate among all subtasks
                          )
    for opr in job_plan:
        oid=opr['id']
        if('inputs' in opr):
            for uopr in opr['inputs']:
                uid=uopr['id']
                JobGraph.add_edge(uid, oid)    #uid->oid
                JobGraph.nodes[uid]['outboundtype']=uopr['ship_strategy']

    getMetricsWarmup(WARMUP*2, JobGraph, _runiter, vertex_ids, job_id)

    toposeq=list(nx.topological_sort(JobGraph))    # topological_sort on operators
    print("topological_sort:    ", toposeq)
    _period=RUNPERD
    #------------------------------------# run a period
    while(_period>0):
        time.sleep(RUNFREQ)
        _period-=RUNFREQ
        print("        ITERATION:", str(_runiter), "PERIOD:", str(_period), "-------------------------------------------------------------")

        #------------------------------------# get cpu utilization metrics for each worker

        # pull cpu util metrics for each worker during experiment phase
        for key, value in workerCpuUtils.items():
            value.append(int(str2float(get_prometheus_cpuutil(jmip, key))*10))
            workerCpuUtils[key] = value

        JobGraphDict=defaultdict(nested_dict)
        for vid in JobGraph.nodes:
            JobGraphDict[vid]['_cpuutil']=np.array([])
            JobGraphDict[vid]['_oip']=np.array([])
            JobGraphDict[vid]['_oop']=np.array([])
            JobGraphDict[vid]['_tip']=np.array([])
            JobGraphDict[vid]['_top']=np.array([])
            JobGraphDict[vid]['_idletime']=np.array([])
            JobGraphDict[vid]['_bkpstime']=np.array([])
            JobGraphDict[vid]['_busytime']=np.array([])
            JobGraphDict[vid]['_ioread']=np.array([])
            JobGraphDict[vid]['_iowrite']=np.array([])
            JobGraphDict[vid]['_oib']=np.array([])
            JobGraphDict[vid]['_oob']=np.array([])
            JobGraphDict[vid]['parallelism']=JobGraph.nodes[vid]['parallelism']
            JobGraphDict[vid]['name']=JobGraph.nodes[vid]['name']

        #------------------------------------# Get profiling data per subtask
        for vid in vertex_ids:    # vid: operator id
            vertix=get_task_vertix_details(jmip, jmpt, job_id, vid)
            #vts=str(vertix['now'])
            _vname=vertix['name']
            vname=_vname.replace(' ','_').replace(',','_').replace(';','_')        # operator name
            #vpall=str(vertix['parallelism'])
            for vtask in vertix['subtasks']:
                ttm=vtask['taskmanager-id']    # taskmanager id of current subtask.  "192.168.1.12:39287-373453"
                tmip=ttm.split(":")[0]
                tid=str(vtask['subtask'])    # subtask id
                # only pull cpu usage for task during profile phase
                st_cpuutil = int(str2float(get_prometheus_cpuutil(jmip, tmip))*10)
                st_busytime = str2int(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.busyTimeMsPerSecond')[0]['value'])
                st_bkpstime = str2int(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.backPressuredTimeMsPerSecond')[0]['value'])
                st_idletime = str2int(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.idleTimeMsPerSecond')[0]['value'])
                st_oip = str2int(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.numRecordsInPerSecond')[0]['value'])
                st_oop = str2int(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.numRecordsOutPerSecond')[0]['value'])
                st_ioread = str2int(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.'+_vname+'.rocksdb_bytes_read')[0]['value'])
                st_iowrite = str2int(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.'+_vname+'.rocksdb_bytes_written')[0]['value'])
                st_oib = str2int(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.numBytesInPerSecond')[0]['value'])
                st_oob = str2int(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.numBytesOutPerSecond')[0]['value'])
                if st_busytime==0:
                    st_busytime=1    # avoid divide 0 error
                st_tip = st_oip / (st_busytime/1000)
                st_top = st_oop / (st_busytime/1000)
                if _DEBUG=="d":
                    print("metric per task:  ", vid,'--------'+vname+'_'+tid+"\n", "busytime", st_busytime, "bkpstime", st_bkpstime, "idletime", st_idletime, "oip", st_oip, "oop", st_oop, "tip", st_tip, "top", st_top)
                JobGraphDict[vid]['_cpuutil']=np.append(JobGraphDict[vid]['_cpuutil'], st_cpuutil)
                JobGraphDict[vid]['_oip']=np.append(JobGraphDict[vid]['_oip'], st_oip)
                JobGraphDict[vid]['_oop']=np.append(JobGraphDict[vid]['_oop'], st_oop)
                JobGraphDict[vid]['_idletime']=np.append(JobGraphDict[vid]['_idletime'], st_idletime)
                JobGraphDict[vid]['_bkpstime']=np.append(JobGraphDict[vid]['_bkpstime'], st_bkpstime)
                JobGraphDict[vid]['_busytime']=np.append(JobGraphDict[vid]['_busytime'], st_busytime)
                JobGraphDict[vid]['_ioread']=np.append(JobGraphDict[vid]['_ioread'], st_ioread)
                JobGraphDict[vid]['_iowrite']=np.append(JobGraphDict[vid]['_iowrite'], st_iowrite)
                JobGraphDict[vid]['_oib']=np.append(JobGraphDict[vid]['_oib'], st_oib)
                JobGraphDict[vid]['_oob']=np.append(JobGraphDict[vid]['_oob'], st_oob)
                JobGraphDict[vid]['_tip']=np.append(JobGraphDict[vid]['_tip'], st_tip)
                JobGraphDict[vid]['_top']=np.append(JobGraphDict[vid]['_top'], st_top)

        #------------------------------------# Calc optimal parallelism with ds2
        for vid in toposeq:    # calc true input/output rate
            parallelism=JobGraphDict[vid]['parallelism']
            JobGraphDict[vid]['cpuutil']=np.mean(JobGraphDict[vid]['_cpuutil'])
            JobGraphDict[vid]['idletime']=np.mean(JobGraphDict[vid]['_idletime'])    # average of all tasks of an operator
            JobGraphDict[vid]['bkpstime']=np.mean(JobGraphDict[vid]['_bkpstime'])
            JobGraphDict[vid]['busytime']=np.mean(JobGraphDict[vid]['_busytime'])
            JobGraphDict[vid]['oip']=np.sum(JobGraphDict[vid]['_oip'])    # sum of all tasks of an operator
            JobGraphDict[vid]['oop']=np.sum(JobGraphDict[vid]['_oop'])
            JobGraphDict[vid]['oib']=np.sum(JobGraphDict[vid]['_oib'])
            JobGraphDict[vid]['oob']=np.sum(JobGraphDict[vid]['_oob'])
            JobGraphDict[vid]['tip']=np.sum(JobGraphDict[vid]['_tip'])
            JobGraphDict[vid]['top']=np.sum(JobGraphDict[vid]['_top'])
            JobGraphDict[vid]['ioread']=np.sum(JobGraphDict[vid]['_ioread'])
            JobGraphDict[vid]['iowrite']=np.sum(JobGraphDict[vid]['_iowrite'])
            if JobGraphDict[vid]['busytime']<0:    # for source operators, busytime == NaN, true_rate == target_input_rate * source_parallelism
                JobGraphDict[vid]['tip']=0
                JobGraphDict[vid]['top']=getCurrentTops()*parallelism    # target_input_rate = src[srcname]*parallelism
                JobGraphDict[vid]['tops']=JobGraphDict[vid]['top']
            if(JobGraphDict[vid]['oip']>0):
                JobGraphDict[vid]['selectivity']=JobGraphDict[vid]['oop']/JobGraphDict[vid]['oip']
            if JobGraphDict[vid]['tip'] == 0:
                JobGraphDict[vid]['tip'] = 1
        for vid in toposeq:    # calc optimal parallelism for current interval
            parallelism=JobGraphDict[vid]['parallelism']
            selectivity=JobGraphDict[vid]['selectivity']
            innodes=JobGraph.nodes[vid]['innodes']
            if(len(innodes)==0):    # source
                JobGraphDict[vid]['optimalparallelism']=parallelism
            else:
                utops=0    # aggregated target output of its all upstream operator
                for uid in innodes:
                    utops+=JobGraphDict[uid]['tops']
                JobGraphDict[vid]['tips']=utops    # target input rate of current operator
                JobGraphDict[vid]['tops']=utops*selectivity    # target output rate of current operator
                JobGraphDict[vid]['optimalparallelism']=math.ceil((utops/(JobGraphDict[vid]['tip']*TARGET_UTIL))*parallelism)
            JobGraph.nodes[vid]['_cpuutil']=np.append(JobGraph.nodes[vid]['_cpuutil'], JobGraphDict[vid]['cpuutil'])
            JobGraph.nodes[vid]['_tops']=np.append(JobGraph.nodes[vid]['_tops'], JobGraphDict[vid]['tops'])
            JobGraph.nodes[vid]['_tips']=np.append(JobGraph.nodes[vid]['_tips'], JobGraphDict[vid]['tips'])
            JobGraph.nodes[vid]['_top']=np.append(JobGraph.nodes[vid]['_top'], JobGraphDict[vid]['top'])
            JobGraph.nodes[vid]['_tip']=np.append(JobGraph.nodes[vid]['_tip'], JobGraphDict[vid]['tip'])
            JobGraph.nodes[vid]['_oop']=np.append(JobGraph.nodes[vid]['_oop'], JobGraphDict[vid]['oop'])
            JobGraph.nodes[vid]['_oip']=np.append(JobGraph.nodes[vid]['_oip'], JobGraphDict[vid]['oip'])
            JobGraph.nodes[vid]['_idletime']=np.append(JobGraph.nodes[vid]['_idletime'], JobGraphDict[vid]['idletime'])
            JobGraph.nodes[vid]['_bkpstime']=np.append(JobGraph.nodes[vid]['_bkpstime'], JobGraphDict[vid]['bkpstime'])
            JobGraph.nodes[vid]['_busytime']=np.append(JobGraph.nodes[vid]['_busytime'], JobGraphDict[vid]['busytime'])
            JobGraph.nodes[vid]['_ioread']=np.append(JobGraph.nodes[vid]['_ioread'], JobGraphDict[vid]['ioread'])
            JobGraph.nodes[vid]['_iowrite']=np.append(JobGraph.nodes[vid]['_iowrite'], JobGraphDict[vid]['iowrite'])
            JobGraph.nodes[vid]['_selectivity']=np.append(JobGraph.nodes[vid]['_selectivity'], JobGraphDict[vid]['selectivity'])
            JobGraph.nodes[vid]['_oob']=np.append(JobGraph.nodes[vid]['_oob'], JobGraphDict[vid]['oob'])
            JobGraph.nodes[vid]['_oib']=np.append(JobGraph.nodes[vid]['_oib'], JobGraphDict[vid]['oib'])
            JobGraph.nodes[vid]['_optimalparallelism']=np.append(JobGraph.nodes[vid]['_optimalparallelism'], JobGraphDict[vid]['optimalparallelism'])
            JobGraph.nodes[vid]['_timestamp']=np.append(JobGraph.nodes[vid]['_timestamp'], time.time())
            # _pertaskdict = pd.DataFrame()
            _pertaskdict = {}
            _pertaskdict['_cpuutil'] = JobGraphDict[vid]['_cpuutil']
            _pertaskdict['_top'] = JobGraphDict[vid]['_top']
            _pertaskdict['_tip'] = JobGraphDict[vid]['_tip']
            _pertaskdict['_oop'] = JobGraphDict[vid]['_oop']
            _pertaskdict['_oip'] = JobGraphDict[vid]['_oip']
            _pertaskdict['_oob'] = JobGraphDict[vid]['_oob']
            _pertaskdict['_oib'] = JobGraphDict[vid]['_oib']
            _pertaskdict['_bkpstime'] = JobGraphDict[vid]['_bkpstime']
            _pertaskdict['_busytime'] = JobGraphDict[vid]['_busytime']
            _pertaskdict['_idletime'] = JobGraphDict[vid]['_idletime']
            JobGraph.nodes[vid]['_pertask'].append([_pertaskdict])

        if _DEBUG=="d":
            for vid in JobGraphDict.keys():
                print("metric per operator:  ", vid, JobGraphDict[vid])

    #------------------------------------# Average optimal parallelism
    for vid in JobGraph.nodes:
        JobGraph.nodes[vid]['cpuutil']=np.mean(JobGraph.nodes[vid]['_cpuutil'])
        JobGraph.nodes[vid]['tips']=np.mean(JobGraph.nodes[vid]['_tips'])
        JobGraph.nodes[vid]['tops']=np.mean(JobGraph.nodes[vid]['_tops'])
        JobGraph.nodes[vid]['top']=np.mean(JobGraph.nodes[vid]['_top'])
        JobGraph.nodes[vid]['tip']=np.mean(JobGraph.nodes[vid]['_tip'])
        JobGraph.nodes[vid]['oop']=np.mean(JobGraph.nodes[vid]['_oop'])
        JobGraph.nodes[vid]['oip']=np.mean(JobGraph.nodes[vid]['_oip'])
        JobGraph.nodes[vid]['idletime']=np.mean(JobGraph.nodes[vid]['_idletime'])
        JobGraph.nodes[vid]['bkpstime']=np.mean(JobGraph.nodes[vid]['_bkpstime'])
        JobGraph.nodes[vid]['busytime']=np.mean(JobGraph.nodes[vid]['_busytime'])
        JobGraph.nodes[vid]['ioread']=np.mean(JobGraph.nodes[vid]['_ioread'])
        JobGraph.nodes[vid]['iowrite']=np.mean(JobGraph.nodes[vid]['_iowrite'])
        JobGraph.nodes[vid]['selectivity']=np.mean(JobGraph.nodes[vid]['_selectivity'])
        JobGraph.nodes[vid]['oob']=np.mean(JobGraph.nodes[vid]['_oob'])
        JobGraph.nodes[vid]['oib']=np.mean(JobGraph.nodes[vid]['_oib'])
        JobGraph.nodes[vid]['optimalparallelism']=math.ceil(np.median(JobGraph.nodes[vid]['_optimalparallelism']))
        JobGraph.nodes[vid]['maxoptimalparallelism']=np.amax(JobGraph.nodes[vid]['_optimalparallelism'])

    run2_top = getCurrentTops()

    # if(_runiter==1):
    #     for vid in JobGraph.nodes:
    #         if(JobGraph.nodes[vid]['oip']==0):
    #             # JobGraph.nodes[vid]['_cpcost']=(JobGraph.nodes[vid]['busytime']/JobGraph.nodes[vid]['oop'])
    #             JobGraph.nodes[vid]['_cpcost']=(JobGraph.nodes[vid]['cpuutil']/JobGraph.nodes[vid]['oop'])
    #             JobGraph.nodes[vid]['_iocost']=((JobGraph.nodes[vid]['ioread']+JobGraph.nodes[vid]['iowrite'])/JobGraph.nodes[vid]['oop'])
    #         else:
    #             # JobGraph.nodes[vid]['_cpcost']=(JobGraph.nodes[vid]['busytime']/JobGraph.nodes[vid]['oip'])    # unit cost per rec
    #             JobGraph.nodes[vid]['_cpcost']=(JobGraph.nodes[vid]['cpuutil']/JobGraph.nodes[vid]['oip'])    # unit cost per rec
    #             JobGraph.nodes[vid]['_iocost']=((JobGraph.nodes[vid]['ioread']+JobGraph.nodes[vid]['iowrite'])/JobGraph.nodes[vid]['oip'])    # unit cost per rec

    #         if(JobGraph.nodes[vid]['oop']==0):
    #             JobGraph.nodes[vid]['_nwcost']=0
    #         else:
    #             JobGraph.nodes[vid]['_nwcost']=(JobGraph.nodes[vid]['oob']/JobGraph.nodes[vid]['oop'])    # unit cost per rec

    # if(_runiter>1):
    for vid in JobGraph.nodes:
        jg=pickle.load(open(COSTPATH, "rb"))
        JobGraph.nodes[vid]['_cpcost']=jg.nodes[vid]['_cpcost']
        JobGraph.nodes[vid]['_nwcost']=jg.nodes[vid]['_nwcost']
        JobGraph.nodes[vid]['_iocost']=jg.nodes[vid]['_iocost']

    for vid in JobGraph.nodes:
        # cost of this operator per subtask
        JobGraph.nodes[vid]['cpcost']=(JobGraph.nodes[vid]['tips']/JobGraph.nodes[vid]['optimalparallelism'])*JobGraph.nodes[vid]['_cpcost']
        JobGraph.nodes[vid]['iocost']=(JobGraph.nodes[vid]['tips']/JobGraph.nodes[vid]['optimalparallelism'])*JobGraph.nodes[vid]['_iocost']/1024/1024
        if(JobGraph.nodes[vid]['tips']==0):
            JobGraph.nodes[vid]['cpcost']=(JobGraph.nodes[vid]['tops']/JobGraph.nodes[vid]['optimalparallelism'])*JobGraph.nodes[vid]['_cpcost']
            JobGraph.nodes[vid]['iocost']=(JobGraph.nodes[vid]['tops']/JobGraph.nodes[vid]['optimalparallelism'])*JobGraph.nodes[vid]['_iocost']/1024/1024
        JobGraph.nodes[vid]['nwcost']=(JobGraph.nodes[vid]['tops']/JobGraph.nodes[vid]['optimalparallelism'])*JobGraph.nodes[vid]['_nwcost']/1024/1024
        # for iocost and nwcost, convert bytes to mb to avoid overflow

    pickle.dump(JobGraph, open(RUNPATH+"/"+str(_runiter)+"_jg.pkl", "wb"))
    pickle.dump(workerCpuUtils, open(RUNPATH+"/"+str(_runiter)+"_cpuutil.pkl", "wb"))

    print("================================")
    # download all Flink log
    logurl=[]
    logurl.append("http://"+jmip+":"+str(jmpt)+"/jobmanager/log")
    for tm in tmidlist:
        for ll in rest_client.taskmanagers.get_logs(tm):
            ln=ll['name']
            if(ln.endswith('.log') or ln.endswith('.out')):
                print(tm, ln)
                logurl.append("http://"+jmip+":"+str(jmpt)+"/taskmanagers/"+tm+"/logs/"+ln)
                # http://192.168.1.105:8081/taskmanagers/192.168.1.153:38019-96b53d/logs/flink-tidb-taskexecutor-0-flink3.log

    print(logurl)
    runcmd('mkdir ./'+RUNPATH+'/'+str(_runiter)+'/')
    for lg in logurl:
        runcmd('wget -P ./'+RUNPATH+'/'+str(_runiter)+' '+lg)
    if(RUNID.startswith('custom')):
        runcmd('cp '+config_file_name+' ./'+RUNPATH+'/'+str(_runiter)+'/')
        runcmd('cp placement_detail ./'+RUNPATH+'/'+str(_runiter)+'/')

    # if(run1_top != run2_top):
    #     print('target_input_rate changed. skip iteration ... ')
    #     # next iteration must recfg

    # recfg at the end of iteration
    src_oop=0
    src_tops=0
    trigger=False
    total_parallelism = 0
    total_optimalparallelism = 0
    for vid in JobGraph.nodes:
        total_parallelism += JobGraph.nodes[vid]['parallelism']
        total_optimalparallelism += JobGraph.nodes[vid]['optimalparallelism']
        if(abs(JobGraph.nodes[vid]['optimalparallelism']-JobGraph.nodes[vid]['parallelism']))>2:
            trigger=True
        if("Source" in JobGraph.nodes[vid]['name']):
            src_oop += JobGraph.nodes[vid]['oop']
            src_tops += JobGraph.nodes[vid]['tops']

    # clean previous savepoint
    runcmd('rm -r '+SAVEROOT+'/savepoint*')
    PASTDURATION += (int(time.time())-DEPLOYTIME)
    print("total duration since last recfg: ", int(time.time())-DEPLOYTIME)
    stopjob(jmip, jmpt, SAVEROOT, 10)
    for lg in logurl:
        runcmd('wget -P ./'+RUNPATH+'/'+str(_runiter)+' '+lg)
    # recfg parallelism from JobGraph.nodes[vid]['optimalparallelism']
    for vid in JobGraph.nodes:
        for _opr in oprlist:
            oprname=list(_opr.keys())[0]
            if(oprname in JobGraph.nodes[vid]['name']):
                print('----', _opr[oprname], JobGraph.nodes[vid]['optimalparallelism'])
                jarargs[_opr[oprname]]=JobGraph.nodes[vid]['optimalparallelism']

    # stop flink
    runcmd('ssh '+user+'@'+jmip+' "cd '+FLINKROOT+'/scripts/ ; python3 deployflink.py '+ctype+' stop"')

    if(total_optimalparallelism>len(iplist)*workers_slot):
        print("Number of submitted tasks ",total_optimalparallelism," > Number of available slots ",len(iplist)*workers_slot)
        sys.exit(-1)

    # change num of TaskManager
    total_TMs = int(math.ceil(total_optimalparallelism/workers_slot))
    workers_ip=iplist[:total_TMs]
    # write worker ips into config file: aws/workers
    with open('aws/workers', 'w') as file:
        for nodeip in workers_ip:
            file.write(nodeip+'\n')

    if(RUNID.startswith('custom')):
        # change placement
        print("====================== calc placement ======================")
        # call micro-benchmark to get the plan
        plan = microBenchmark(workers_ip, workers_slot, paras, randomOptimal, JobGraph)
        #------------------------------------#  Generate placement config file
        print("======== Placement plan found:")
        selectedPlan = plan
        print(plan)
        print("======== config_file_name: "+config_file_name)
        workerIdx = 0
        f = open(config_file_name, "w")
        for k,v in plan.items():
            for i in range(v.num):
                for _task in k.list:
                    task=mapping[_task]
                    ff=task+"; "+workers_ip[workerIdx]
                    print(ff)
                    f.write(ff+"\n")
                workerIdx+=1
        f.close()
        place_detail_file = open('placement_detail', 'w')
        place_detail_file.write('\n')
        for key, value in selectedPlan.items():
            place_detail_file.write(str(key)+' '+str(value)+'\n')
        place_detail_file.close()

    print("jarargs", jarargs)
    # restart Flink (not vpc) and resubmit job
    runcmd('ssh '+user+'@'+jmip+' "cd '+FLINKROOT+'/scripts/ ; python3 deployflink.py '+ctype+' start"')
    runsleep(30, 10)    # wait for deployment finishing
    rest_client = FlinkRestClient.get(host=jmip, port=jmpt)
    rest_client.overview()
    ur=upload_jar(jmip, jmpt, jarpath)
    jar_id = ur['filename'].split('/')[-1]
    startsubmittedjob(jmip, jmpt, jarargs, SAVEROOT, 10, True)
    DEPLOYTIME=int(time.time())


if __name__ == '__main__':

    # start with custom placement
    changeConfigFileOnScheduling("custom")
    f = open(config_file_name, "w")
    for ff in schedulercfg1st:
        f.write(ff+"\n")
    f.close()

    # write worker ips into config file: aws/workers
    with open('aws/workers', 'w') as file:
        for nodeip in workers_ip:
            file.write(nodeip+'\n')
    
    if(tcmd=='stop'):
        resetvpc(jmip, user, FLINKROOT, TMPROOT, SAVEROOT, ctype, iplist, resetsec, tcnic)
        exit()

    # clean previous savepoint
    runcmd('rm -r '+SAVEROOT+'/savepoint*')
    # start with a given placement && parallelism for 1st iteration
    if(tcmd=='start'):
        job_id=startjob(jmip, jmpt, user, FLINKROOT, TMPROOT, SAVEROOT, iplist, resetsec, ctype, jarpath, jarargs, tcnic, tclimit, iolimit, fromsavepoint, 10)
    DEPLOYTIME=int(time.time())
    PASTDURATION=0

    # ID of current exp
    RUNPATH=fjson.split('/')[-1].replace('.','')+'_'+RUNID
    runcmd("mkdir ./"+RUNPATH)

    f = open('./'+RUNPATH+'/DEPLOYTIME', "w")
    f.write(str(DEPLOYTIME))
    f.close()
    
    
    if(RUNID.startswith('custom')):
        changeConfigFileOnScheduling("custom")
    elif(RUNID.startswith('even')):
        changeConfigFileOnScheduling("even")
    elif(RUNID.startswith('random')):
        changeConfigFileOnScheduling("random")
      

    for _itr in range(1, NUMITER+1):
        rundynamic(_itr)


