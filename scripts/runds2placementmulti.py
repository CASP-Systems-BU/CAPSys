# python3 runds2placementmulti.py expjson/multi.json start runmulti -1 custom

from dfsMultiProcess import *
from exputils import *
import random

def custom_formatter(x):
    return f"{x:.2f}"

np.set_printoptions(threshold=np.inf, linewidth=np.inf, edgeitems=10)
np.set_printoptions(formatter={'all': custom_formatter})


# output config file name
config_file_name = 'schedulercfg'

# wait some time to warm up
WARMUP=3*60
WARMUP1ST=20*60
# activation time: period(sec) of each iteration
RUNPERD=4*60
# policy interval: frequency of profiling in each period
RUNFREQ=5

TARGET_UTIL=0.7

#------------------------------------# get cmd argument
fjson=sys.argv[1]
tcmd=sys.argv[2]
RUNID=sys.argv[3]
RUNITER=int(sys.argv[4])
POLICY = sys.argv[5]

_DEBUG=""
if(len(sys.argv)>5):
    _DEBUG=sys.argv[5]


#------------------------------------# read json and get job configuration
cfg=json.loads(open(fjson,'r').read())
expname=cfg['expname']
iplist=cfg['iplist']
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
# num of slots per worker
workers_slot=cfg['workers_slot']

# per job cfgs
jobscfg=cfg['jobs']
random.shuffle(jobscfg)

srcratelistall=[]
for jcfg in jobscfg:
    jarpath=jcfg['jarpath']
    jarargs=jcfg['jarargs']
    SAVEDIR=jcfg['SAVEDIR']
    srcratelist=jcfg['srcratelist']    # target_input_rate
    srcratelistall = srcratelistall + srcratelist
    oprlist=jcfg['oprlist']    # flink job parameters that tunes parallelism
    mapping=jcfg['mapping']    # mapping of operator name from flink_metrics to schedulercfg
    schedulercfg1st=jcfg['schedulercfg1st']
    # # Configurable parameters to tune the dfs threshold
    # planNum = cfg['dfs']['planNum']
    # step_ratio_compute = cfg['dfs']['step_ratio_compute']
    # step_ratio_io = cfg['dfs']['step_ratio_io']
    # step_ratio_network = cfg['dfs']['step_ratio_network']
    # randomOptimal = cfg['dfs']['randomOptimal']
    # paras = MicrobenchmarkParas(planNum, step_ratio_compute, step_ratio_io, step_ratio_network)



# # warmup for stateful query
# if(SAVEROOT!=""):
#     WARMUP1ST=1800

def runds2placement(RUNITER, RUNID):
    # Terminate the Flink cluster based on the old setting
    runcmd("python3 deployflink.py aws stop")
    
    # ID of current exp
    RUNPATH=fjson.split('/')[-1].replace('.','')+'_'+RUNID+'_iter'+str(RUNITER)
    RUNPROFILE=fjson.split('/')[-1].replace('.','')+'_profile_iter0'

    # worker ips
    workers_ip=iplist
    # write worker ips into config file: aws/workers
    with open('aws/workers', 'w') as file:
        for nodeip in workers_ip:
            file.write(nodeip+'\n')
    # initiate a map of workers: pull cpu util metrics
    workerCpuUtils = {}
    for ip in workers_ip:
        workerCpuUtils[ip] = []


    #------------------------------------# additional commands to stop/start the job
#     if(tcmd=='stop'):
#         resetvpc(jmip, user, FLINKROOT, TMPROOT, SAVEROOT, ctype, iplist, resetsec, tcnic)
#         exit()
#     if(tcmd=='start'):
#         job_id=startjob(jmip, jmpt, user, FLINKROOT, TMPROOT, SAVEROOT, iplist, resetsec, ctype, jarpath, jarargs, tcnic, tclimit, iolimit, fromsavepoint)

    initjm(jmip, user, FLINKROOT, ctype, iplist)
    resetvpc(jmip, user, FLINKROOT, TMPROOT, SAVEROOT, ctype, iplist, resetsec, tcnic)
    # restart Flink (not vpc) and resubmit job
    runcmd('ssh '+user+'@'+jmip+' "cd '+FLINKROOT+'/scripts/ ; python3 deployflink.py '+ctype+' start"')
    runsleep(30, 10)    # wait for deployment finishing
    rest_client = FlinkRestClient.get(host=jmip, port=jmpt)
    rest_client.overview()

    for jcfg in jobscfg:
        jarpath=jcfg['jarpath']
        jarargs=jcfg['jarargs']
        SAVEDIR=jcfg['SAVEDIR']
        srcratelist=jcfg['srcratelist']    # target_input_rate
        oprlist=jcfg['oprlist']    # flink job parameters that tunes parallelism
        mapping=jcfg['mapping']    # mapping of operator name from flink_metrics to schedulercfg
        schedulercfg1st=jcfg['schedulercfg1st']
        fromsavepoint=True
        if(RUNITER==0):    # RUNITER==0: profile
            fromsavepoint=False
        if(RUNITER<=0):    # RUNITER<0: apply given placement and run (with savepoint applied)
            f = open(config_file_name, "w")
            for ff in schedulercfg1st:
                f.write(ff+"\n")
            f.close()
        if(RUNITER>0):    # RUNITER>0: calculate placement based on profile and run (with savepoint applied)
            pass          # todo: read profile data, call go program and get placement
        print(jarpath)
        ur=upload_jar(jmip, jmpt, jarpath)
        jar_id = ur['filename'].split('/')[-1]
        startsubmittedjob(jmip, jmpt, jarargs, SAVEDIR, 10, True, jar_id)

    runcmd("mkdir ./"+RUNPATH)


    print("wait some time to warm up")
    if(RUNITER==0):
        runsleep(WARMUP1ST, 30)
    else:
        runsleep(WARMUP, 30)


    #------------------------------------# get job info
    rest_client = FlinkRestClient.get(host=jmip, port=jmpt)
    rest_client.overview()
    JobGraphAll={}
    for jobs in rest_client.jobs.overview():
        job_id = jobs['jid']
        job_name = jobs['name']
        vertex_ids=rest_client.jobs.get_vertex_ids(job_id)
        job = rest_client.jobs.get(job_id=job_id)

        tmidlist=[]
        for tm in rest_client.taskmanagers.all():
            tmidlist.append(tm['id'])


        #------------------------------------# generate logical dataflow
        print("starting......    job_id:", job_id, "    job_name:", job_name)
        job_plan=get_job_plan_details(jmip, jmpt, job_id)['plan']['nodes']
        print("job_plan:  ", job_plan)
        JobGraphAll[job_name]=nx.DiGraph()
        for opr in job_plan:
            oname=opr['description'].replace(' ','_').replace('+','_').replace('-','_').replace(',','_').replace(':','_').replace(';','_').replace('<br/>','').replace('(','_').replace(')','_')
            innodes=[x['id'] for x in opr['inputs']] if ('inputs' in opr) else []
            JobGraphAll[job_name].add_node(opr['id'], parallelism=opr['parallelism'], name=oname, pname=oname,    # vid, parallelism, name of current operator, name to be printed in schedulercfg
                              innodes=innodes,    # vid of upstream operators
                              outboundtype="",    # outbound link type (REBALANCE/HASH/FORWARD)
                              _ttm=np.array([]), _cpuutil=np.array([]), cpuutil=0,
                              _oip=np.array([]), _oop=np.array([]), _tip=np.array([]), _top=np.array([]), _tops=np.array([]), _tips=np.array([]),
                              _busytime=np.array([]), _bkpstime=np.array([]), _idletime=np.array([]), _selectivity=np.array([]),
                              _optimalparallelism=np.array([]), _ioread=np.array([]), _iowrite=np.array([]), _oib=np.array([]), _oob=np.array([]),
                              _pertask=[],
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
                    JobGraphAll[job_name].add_edge(uid, oid)    #uid->oid
                    JobGraphAll[job_name].nodes[uid]['outboundtype']=uopr['ship_strategy']


    _period=RUNPERD
    _numperiod=RUNPERD/RUNFREQ
    #------------------------------------# run a period
    while(_period>0):
        time.sleep(RUNFREQ)
        _period-=RUNFREQ
        for jobs in rest_client.jobs.overview():
            job_id = jobs['jid']
            job_name = jobs['name']
            vertex_ids=rest_client.jobs.get_vertex_ids(job_id)
            job = rest_client.jobs.get(job_id=job_id)
            toposeq=list(nx.topological_sort(JobGraphAll[job_name]))    # topological_sort on operators
            # print("topological_sort:    ", toposeq)
            print("        job_name:", job_name, "  ITERATION:", RUNITER, "PERIOD:", _period, "-------------------------------------------------------------")

            #------------------------------------# get cpu utilization metrics for each worker

            # pull cpu util metrics for each worker during experiment phase
            if (RUNITER==1):
                for key, value in workerCpuUtils.items():
                    value.append(int(str2float(get_prometheus_cpuutil(jmip, key))*10))
                    workerCpuUtils[key] = value

            JobGraphDict=defaultdict(nested_dict)
            for vid in JobGraphAll[job_name].nodes:
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
                JobGraphDict[vid]['parallelism']=JobGraphAll[job_name].nodes[vid]['parallelism']
                JobGraphDict[vid]['name']=JobGraphAll[job_name].nodes[vid]['name']

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
                    st_cpuutil = -1
                    if (RUNITER==0):
                        st_cpuutil = int(str2float(get_prometheus_cpuutil(jmip, tmip))*10)
                    fieldlist = [
                        tid+'.busyTimeMsPerSecond',
                        tid+'.backPressuredTimeMsPerSecond',
                        tid+'.idleTimeMsPerSecond',
                        tid+'.numRecordsInPerSecond',
                        tid+'.numRecordsOutPerSecond',
                        tid+'.'+_vname+'.rocksdb_bytes_read',
                        tid+'.'+_vname+'.rocksdb_bytes_written',
                        tid+'.numBytesInPerSecond',
                        tid+'.numBytesOutPerSecond'
                    ]
                    st_res = get_task_metrics_details_multiple(jmip, jmpt, job_id, vid, fieldlist)
                    st_busytime = str2int(st_res[tid+'.busyTimeMsPerSecond'])
                    st_bkpstime = str2int(st_res[tid+'.backPressuredTimeMsPerSecond'])
                    st_idletime = str2int(st_res[tid+'.idleTimeMsPerSecond'])
                    st_oip = str2int(st_res[tid+'.numRecordsInPerSecond'])
                    st_oop = str2int(st_res[tid+'.numRecordsOutPerSecond'])
                    st_ioread = str2int(st_res[tid+'.'+_vname+'.rocksdb_bytes_read'])
                    st_iowrite = str2int(st_res[tid+'.'+_vname+'.rocksdb_bytes_written'])
                    st_oib = str2int(st_res[tid+'.numBytesInPerSecond'])
                    st_oob = str2int(st_res[tid+'.numBytesOutPerSecond'])
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
                    for src in srcratelistall:
                        srcname=list(src.keys())[0]
                        if(srcname in JobGraphAll[job_name].nodes[vid]['name']):
                            JobGraphDict[vid]['top']=src[srcname]*parallelism       # no need for this line
                            JobGraphDict[vid]['tops']=JobGraphDict[vid]['top']
                if(JobGraphDict[vid]['oip']>0):
                    JobGraphDict[vid]['selectivity']=JobGraphDict[vid]['oop']/JobGraphDict[vid]['oip']
                if JobGraphDict[vid]['tip'] == 0:
                    JobGraphDict[vid]['tip'] = 1
            for vid in toposeq:    # calc optimal parallelism for current interval
                parallelism=JobGraphDict[vid]['parallelism']
                selectivity=JobGraphDict[vid]['selectivity']
                innodes=JobGraphAll[job_name].nodes[vid]['innodes']
                if(len(innodes)==0):    # source
                    JobGraphDict[vid]['optimalparallelism']=parallelism
                else:
                    utops=0    # aggregated target output of its all upstream operator
                    for uid in innodes:
                        utops+=JobGraphDict[uid]['tops']
                    JobGraphDict[vid]['tips']=utops    # target input rate of current operator
                    JobGraphDict[vid]['tops']=utops*selectivity    # target output rate of current operator
                    JobGraphDict[vid]['optimalparallelism']=math.ceil((utops/(JobGraphDict[vid]['tip']*TARGET_UTIL))*parallelism)
                JobGraphAll[job_name].nodes[vid]['_cpuutil']=np.append(JobGraphAll[job_name].nodes[vid]['_cpuutil'], JobGraphDict[vid]['cpuutil'])
                JobGraphAll[job_name].nodes[vid]['_tops']=np.append(JobGraphAll[job_name].nodes[vid]['_tops'], JobGraphDict[vid]['tops'])
                JobGraphAll[job_name].nodes[vid]['_tips']=np.append(JobGraphAll[job_name].nodes[vid]['_tips'], JobGraphDict[vid]['tips'])
                JobGraphAll[job_name].nodes[vid]['_top']=np.append(JobGraphAll[job_name].nodes[vid]['_top'], JobGraphDict[vid]['top'])
                JobGraphAll[job_name].nodes[vid]['_tip']=np.append(JobGraphAll[job_name].nodes[vid]['_tip'], JobGraphDict[vid]['tip'])
                JobGraphAll[job_name].nodes[vid]['_oop']=np.append(JobGraphAll[job_name].nodes[vid]['_oop'], JobGraphDict[vid]['oop'])
                JobGraphAll[job_name].nodes[vid]['_oip']=np.append(JobGraphAll[job_name].nodes[vid]['_oip'], JobGraphDict[vid]['oip'])
                JobGraphAll[job_name].nodes[vid]['_idletime']=np.append(JobGraphAll[job_name].nodes[vid]['_idletime'], JobGraphDict[vid]['idletime'])
                JobGraphAll[job_name].nodes[vid]['_bkpstime']=np.append(JobGraphAll[job_name].nodes[vid]['_bkpstime'], JobGraphDict[vid]['bkpstime'])
                JobGraphAll[job_name].nodes[vid]['_busytime']=np.append(JobGraphAll[job_name].nodes[vid]['_busytime'], JobGraphDict[vid]['busytime'])
                JobGraphAll[job_name].nodes[vid]['_ioread']=np.append(JobGraphAll[job_name].nodes[vid]['_ioread'], JobGraphDict[vid]['ioread'])
                JobGraphAll[job_name].nodes[vid]['_iowrite']=np.append(JobGraphAll[job_name].nodes[vid]['_iowrite'], JobGraphDict[vid]['iowrite'])
                JobGraphAll[job_name].nodes[vid]['_selectivity']=np.append(JobGraphAll[job_name].nodes[vid]['_selectivity'], JobGraphDict[vid]['selectivity'])
                JobGraphAll[job_name].nodes[vid]['_oob']=np.append(JobGraphAll[job_name].nodes[vid]['_oob'], JobGraphDict[vid]['oob'])
                JobGraphAll[job_name].nodes[vid]['_oib']=np.append(JobGraphAll[job_name].nodes[vid]['_oib'], JobGraphDict[vid]['oib'])
                JobGraphAll[job_name].nodes[vid]['_optimalparallelism']=np.append(JobGraphAll[job_name].nodes[vid]['_optimalparallelism'], JobGraphDict[vid]['optimalparallelism'])
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
                JobGraphAll[job_name].nodes[vid]['_pertask'].append([_pertaskdict])

            if _DEBUG=="d":
                for vid in JobGraphDict.keys():
                    print("metric per operator:  ", vid, JobGraphDict[vid])


    for jobs in rest_client.jobs.overview():
        job_id = jobs['jid']
        job_name = jobs['name']
        toposeq=list(nx.topological_sort(JobGraphAll[job_name]))    # topological_sort on operators
        #------------------------------------# Average optimal parallelism
        for vid in JobGraphAll[job_name].nodes:
            JobGraphAll[job_name].nodes[vid]['cpuutil']=np.mean(JobGraphAll[job_name].nodes[vid]['_cpuutil'])
            JobGraphAll[job_name].nodes[vid]['tips']=np.mean(JobGraphAll[job_name].nodes[vid]['_tips'])
            JobGraphAll[job_name].nodes[vid]['tops']=np.mean(JobGraphAll[job_name].nodes[vid]['_tops'])
            JobGraphAll[job_name].nodes[vid]['top']=np.mean(JobGraphAll[job_name].nodes[vid]['_top'])
            JobGraphAll[job_name].nodes[vid]['tip']=np.mean(JobGraphAll[job_name].nodes[vid]['_tip'])
            JobGraphAll[job_name].nodes[vid]['oop']=np.mean(JobGraphAll[job_name].nodes[vid]['_oop'])
            JobGraphAll[job_name].nodes[vid]['oip']=np.mean(JobGraphAll[job_name].nodes[vid]['_oip'])
            JobGraphAll[job_name].nodes[vid]['idletime']=np.mean(JobGraphAll[job_name].nodes[vid]['_idletime'])
            JobGraphAll[job_name].nodes[vid]['bkpstime']=np.mean(JobGraphAll[job_name].nodes[vid]['_bkpstime'])
            JobGraphAll[job_name].nodes[vid]['busytime']=np.mean(JobGraphAll[job_name].nodes[vid]['_busytime'])
            JobGraphAll[job_name].nodes[vid]['ioread']=np.mean(JobGraphAll[job_name].nodes[vid]['_ioread'])
            JobGraphAll[job_name].nodes[vid]['iowrite']=np.mean(JobGraphAll[job_name].nodes[vid]['_iowrite'])
            JobGraphAll[job_name].nodes[vid]['selectivity']=np.mean(JobGraphAll[job_name].nodes[vid]['_selectivity'])
            JobGraphAll[job_name].nodes[vid]['oob']=np.mean(JobGraphAll[job_name].nodes[vid]['_oob'])
            JobGraphAll[job_name].nodes[vid]['oib']=np.mean(JobGraphAll[job_name].nodes[vid]['_oib'])
            JobGraphAll[job_name].nodes[vid]['optimalparallelism']=math.ceil(np.mean(JobGraphAll[job_name].nodes[vid]['_optimalparallelism']))
            JobGraphAll[job_name].nodes[vid]['maxoptimalparallelism']=np.amax(JobGraphAll[job_name].nodes[vid]['_optimalparallelism'])

        # for vid in JobGraphAll[job_name].nodes:
        #     parallelism=JobGraphAll[job_name].nodes[vid]['parallelism']
        #     innodes=JobGraphAll[job_name].nodes[vid]['innodes']
        #     if(len(innodes)!=0):    # not source
        #         utops=0
        #         for uid in innodes:
        #             utops+=JobGraphAll[job_name].nodes[uid]['tops']
        #         JobGraphAll[job_name].nodes[vid]['optimalparallelism']=math.ceil((utops/JobGraphAll[job_name].nodes[vid]['tip'])*parallelism)


        if(RUNITER<=0):
            for vid in JobGraphAll[job_name].nodes:
                if(JobGraphAll[job_name].nodes[vid]['oip']==0):
                    # JobGraphAll[job_name].nodes[vid]['_cpcost']=(JobGraphAll[job_name].nodes[vid]['busytime']/JobGraphAll[job_name].nodes[vid]['oop'])
                    JobGraphAll[job_name].nodes[vid]['_cpcost']=(JobGraphAll[job_name].nodes[vid]['cpuutil']/JobGraphAll[job_name].nodes[vid]['oop'])
                    JobGraphAll[job_name].nodes[vid]['_iocost']=((JobGraphAll[job_name].nodes[vid]['ioread']+JobGraphAll[job_name].nodes[vid]['iowrite'])/JobGraphAll[job_name].nodes[vid]['oop'])
                else:
                    # JobGraphAll[job_name].nodes[vid]['_cpcost']=(JobGraphAll[job_name].nodes[vid]['busytime']/JobGraphAll[job_name].nodes[vid]['oip'])    # unit cost per rec
                    JobGraphAll[job_name].nodes[vid]['_cpcost']=(JobGraphAll[job_name].nodes[vid]['cpuutil']/JobGraphAll[job_name].nodes[vid]['oip'])    # unit cost per rec
                    JobGraphAll[job_name].nodes[vid]['_iocost']=((JobGraphAll[job_name].nodes[vid]['ioread']+JobGraphAll[job_name].nodes[vid]['iowrite'])/JobGraphAll[job_name].nodes[vid]['oip'])    # unit cost per rec

                if(JobGraphAll[job_name].nodes[vid]['oop']==0):
                    JobGraphAll[job_name].nodes[vid]['_nwcost']=0
                else:
                    JobGraphAll[job_name].nodes[vid]['_nwcost']=(JobGraphAll[job_name].nodes[vid]['oob']/JobGraphAll[job_name].nodes[vid]['oop'])    # unit cost per rec

        if(RUNITER>0):
            for vid in JobGraphAll[job_name].nodes:
                jg=pickle.load(open(RUNPROFILE+"/jg.pkl", "rb"))
                JobGraphAll[job_name].nodes[vid]['_cpcost']=jg.nodes[vid]['_cpcost']
                JobGraphAll[job_name].nodes[vid]['_nwcost']=jg.nodes[vid]['_nwcost']
                JobGraphAll[job_name].nodes[vid]['_iocost']=jg.nodes[vid]['_iocost']

        for vid in JobGraphAll[job_name].nodes:
            # cost of this operator per subtask
            JobGraphAll[job_name].nodes[vid]['cpcost']=(JobGraphAll[job_name].nodes[vid]['tips']/JobGraphAll[job_name].nodes[vid]['optimalparallelism'])*JobGraphAll[job_name].nodes[vid]['_cpcost']
            JobGraphAll[job_name].nodes[vid]['iocost']=(JobGraphAll[job_name].nodes[vid]['tips']/JobGraphAll[job_name].nodes[vid]['optimalparallelism'])*JobGraphAll[job_name].nodes[vid]['_iocost']/1024/1024
            if(JobGraphAll[job_name].nodes[vid]['tips']==0):
                JobGraphAll[job_name].nodes[vid]['cpcost']=(JobGraphAll[job_name].nodes[vid]['tops']/JobGraphAll[job_name].nodes[vid]['optimalparallelism'])*JobGraphAll[job_name].nodes[vid]['_cpcost']
                JobGraphAll[job_name].nodes[vid]['iocost']=(JobGraphAll[job_name].nodes[vid]['tops']/JobGraphAll[job_name].nodes[vid]['optimalparallelism'])*JobGraphAll[job_name].nodes[vid]['_iocost']/1024/1024
            JobGraphAll[job_name].nodes[vid]['nwcost']=(JobGraphAll[job_name].nodes[vid]['tops']/JobGraphAll[job_name].nodes[vid]['optimalparallelism'])*JobGraphAll[job_name].nodes[vid]['_nwcost']/1024/1024
            # for iocost and nwcost, convert bytes to mb to avoid overflow

        pickle.dump(JobGraphAll[job_name], open(RUNPATH+"/jg_"+job_name+".pkl", "wb"))

        # store the cpu util metrics in a different file
        if (RUNITER==1):
            pickle.dump(workerCpuUtils, open(RUNPATH+"/cpuutil.pkl", "wb"))

        print("====================== logical dataflow ======================")
        for ge in JobGraphAll[job_name].edges.items():
            print("---- edge: ", ge)
        for gn in JobGraphAll[job_name].nodes.items():
            print("---- node: ",gn[0], gn[1]['name'], '    parallelism', gn[1]['parallelism'], "\n",
                  '    busytime', gn[1]['busytime'], '    bkpstime', gn[1]['bkpstime'], '    idletime', gn[1]['idletime'], "\n",
                  '    tip', gn[1]['tip'], '    top', gn[1]['top'], "\n",
                  '    oip', gn[1]['oip'], '    oop', gn[1]['oop'], "\n",
                  '    tips', gn[1]['tips'], '    tops', gn[1]['tops'], "\n",
                  '    optimalparallelism', gn[1]['optimalparallelism'], "\n",
                  '    _cpcost', gn[1]['_cpcost'],'    cpcost', gn[1]['cpcost'], "\n",
                  '    _nwcost', gn[1]['_nwcost'],'    nwcost', gn[1]['nwcost'], "\n",
                  '    _iocost', gn[1]['_iocost'],'    iocost', gn[1]['iocost'], "\n")


    print("================================")
    # download all Flink log
    logurl=[]
    logurl.append("http://"+jmip+":"+str(jmpt)+"/jobmanager/log")
    for tm in tmidlist:
        for ll in rest_client.taskmanagers.get_logs(tm):
            ln=ll['name']
            if(ln.endswith('.log')):
                print(tm, ln)
                logurl.append("http://"+jmip+":"+str(jmpt)+"/taskmanagers/"+tm+"/logs/"+ln)
                # http://192.168.1.105:8081/taskmanagers/192.168.1.153:38019-96b53d/logs/flink-tidb-taskexecutor-0-flink3.log

    print(logurl)
    for lg in logurl:
        runcmd('wget -P ./'+RUNPATH+'/ '+lg)

#     if(RUNITER==0 and SAVEROOT!=""):
#         createJobSavepoint(user, jmip, jmpt, job_id, SAVEROOT)


runds2placement(RUNITER, RUNID)
