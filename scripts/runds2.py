from flink_rest_client import FlinkRestClient
import sys, os, time, json, requests, json
import networkx as nx
resetsec=180
retry=5

# python3 runds2.py 0 expjson/q8m_a.json collect/start/stop

_DEBUG=sys.argv[1]
fjson=sys.argv[2]
tcmd=sys.argv[3]

cfg=json.loads(open(fjson,'r').read())
jarpath=cfg['jarpath']
jarargs=cfg['jarargs']
expname=cfg['expname']
iplist=cfg['iplist']
jmip=cfg['jmip']
kafkaip=cfg['kafkaip']
KAFKAROOT=cfg['KAFKAROOT']
tclimit=cfg['tclimit']
tcnic=cfg['tcnic']
user=cfg['user']
jmpt=cfg['jmpt']
FLINKROOT=cfg['FLINKROOT']
TMPROOT=cfg['TMPROOT']
ctype=cfg['ctype']
resetsec=cfg['resetsec']
srcratelist=cfg['srcratelist']    # target_input_rate

def str2int(str):
    if(str=='NaN'):
        return(-1)
    fstr=float(str)
    istr=int(fstr)
    istr=max(0, istr)
    return(istr)

def runsleep(dur, tik):
    cnt=int(dur)
    while(cnt>0):
        print('sleeping... ',cnt)
        time.sleep(int(tik))
        cnt-=int(tik)

def runcmd(cmd):
    print('------------------------------------------------------------')
    print(cmd)
    res=os.popen(cmd).read()
    print('------------------------------------------------------------')
    return(res)

def get_task_metrics_details(jobid, taskid, fieldid):
    # http://192.168.1.105:8081/jobs/e81ee095a99bfc431e260d044ff7e03d/vertices/ea632d67b7d595e5b851708ae9ad79d6/metrics?get=4.busyTimeMsPerSecond
    url = "http://"+jmip+":"+str(jmpt)+"/jobs/{}/vertices/{}/metrics?get={}".format(jobid, taskid, fieldid)
    response = requests.get(url)
    response.raise_for_status()
    ans=response.json()#[0]['value']
    return(ans)

def get_job_plan_details(jobid):
    # http://192.168.1.105:8081/jobs/e81ee095a99bfc431e260d044ff7e03d/plan
    url = "http://"+jmip+":"+str(jmpt)+"/jobs/{}/plan".format(jobid)
    response = requests.get(url)
    response.raise_for_status()
    ans=response.json()#[0]['value']
    return(ans)

def get_taskmanager_metrics_details(tmid, fieldid):
    # http://192.168.1.180:8081/taskmanagers/192.168.1.181:43893-b21053/metrics
    url = "http://"+jmip+":"+str(jmpt)+"/taskmanagers/{}/metrics?get={}".format(tmid, fieldid)
    response = requests.get(url)
    response.raise_for_status()
    ans=response.json()#[0]['value']
    return(ans)

def upload_jar(fpath):
    fname=fpath.split('/')[-1]
    print(fname)
    jfile = {"file": (fname, (open(fpath, "rb")), "application/x-java-archive")}
    url="http://"+jmip+":"+str(jmpt)+"/jars/upload"
    response = requests.request(method="POST", url=url, files=jfile)
    return(response.json())

def resetvpc():
    runcmd('ssh '+user+'@'+jmip+' "cd '+FLINKROOT+'/scripts/ ; python3 deployflink.py '+ctype+' stop"')
    for ip in iplist:
        runcmd('ssh '+user+'@'+ip+' "sudo reboot"')
    runsleep(resetsec, 10)
    runcmd('cd ~/; python3 ec2tools.py mountall')
    for ip in iplist:
        runcmd('ssh '+user+'@'+ip+' "rm -rf '+TMPROOT+' ; mkdir '+TMPROOT+' "')
        runcmd('ssh '+user+'@'+ip+' "mkdir '+TMPROOT+'/flinkstate"')
        #runcmd('ssh '+user+'@'+ip+' "sudo systemctl restart systemd-timesyncd.service"')
        # sudo systemctl status systemd-timesyncd.service

def initjm():
    runcmd('ssh '+user+'@'+jmip+' "mkdir '+FLINKROOT+'"')
    runcmd('scp -r ../scripts'+' '+user+'@'+jmip+':'+FLINKROOT+'/')
    runcmd('scp -r ../flink-dist'+' '+user+'@'+jmip+':'+FLINKROOT+'/')
    for ip in iplist:
        runcmd('ssh '+user+'@'+ip+' "mkdir '+FLINKROOT+'"')
        runcmd('scp -r ../scripts'+' '+user+'@'+ip+':'+FLINKROOT+'/')

def startjob():
    initjm()
    resetvpc()
    runcmd('ssh '+user+'@'+jmip+' "cd '+FLINKROOT+'/scripts/ ; python3 deployflink.py '+ctype+' start"')
    runsleep(30, 10)    # wait for deployment finishing
    rest_client = FlinkRestClient.get(host=jmip, port=jmpt)
    rest_client.overview()
    ur=upload_jar(jarpath)
    jar_id = ur['filename'].split('/')[-1]
    job_id = rest_client.jars.run(jar_id, arguments=jarargs)
    print("deployed...")
    runsleep(60, 10)    # run job for a while before recording
    return(job_id)


# additional commands to stop/start the hob
if(tcmd=='stop'):
    resetvpc()
    exit()
if(tcmd=='start'):
    job_id=startjob()


# get job info
rest_client = FlinkRestClient.get(host=jmip, port=jmpt)
rest_client.overview()
job_id = rest_client.jobs.all()[0]['id']
job = rest_client.jobs.get(job_id=job_id)

tmidlist=[]
for tm in rest_client.taskmanagers.all():
    tmidlist.append(tm['id'])

print("starting......  job_id:", job_id)
job_plan=get_job_plan_details(job_id)['plan']['nodes']
print(job_plan)
JobGraph=nx.DiGraph()    # logical dataflow
for opr in job_plan:
    oname=opr['description'].replace(' ','_').replace('&gt;','>').replace(',','_').replace(';','_')
    innodes=[x['id'] for x in opr['inputs']] if ('inputs' in opr) else []
    JobGraph.add_node(opr['id'], parallelism=opr['parallelism'], name=oname,    # vid, parallelism, name of current operator
        innodes=innodes,    # vid of upstream operators
        oip=0, oop=0,    # aggregated observed input/output rate among all subtasks
        tip=0, top=0,    # aggregated true input/output rate among all subtasks
        busytime=0, bkpstime=0, idletime=0, selectivity=0.0,    # average of metric among all subtasks
        optimalparallelism=0
    )
for opr in job_plan:
    oid=opr['id']
    if('inputs' in opr):
        for uopr in opr['inputs']:
            uid=uopr['id']
            JobGraph.add_edge(uid, oid)    #uid->oid


clock=40*60    # run 40min
while(clock>0):
    print("clock", clock, "-------------------------------------------------------------")
    for vid in JobGraph.nodes:
        JobGraph.nodes[vid]['oip']=0
        JobGraph.nodes[vid]['oop']=0
        JobGraph.nodes[vid]['idletime']=0
        JobGraph.nodes[vid]['bkpstime']=0
        JobGraph.nodes[vid]['busytime']=0
    vertex_ids=rest_client.jobs.get_vertex_ids(job_id)
    for vid in vertex_ids:    # vid: operator id
        jvurl="http://"+jmip+":"+str(jmpt)+"/jobs/"+job_id+"/vertices/"+vid
        res=requests.get(jvurl).json()
        #vts=str(res['now'])
        vname=res['name'].replace(' ','_').replace(',','_').replace(';','_')    # operator name
        #vpall=str(res['parallelism'])
        for vtask in res['subtasks']:
            ttm=vtask['taskmanager-id']    # taskmanager id of current subtask
            tid=str(vtask['subtask'])    # subtask id
            st_busytime=get_task_metrics_details(job_id, vid, tid+'.busyTimeMsPerSecond')[0]
            st_bkpstime=get_task_metrics_details(job_id, vid, tid+'.backPressuredTimeMsPerSecond')[0]
            st_idletime=get_task_metrics_details(job_id, vid, tid+'.idleTimeMsPerSecond')[0]
            st_oip=get_task_metrics_details(job_id, vid, tid+'.numRecordsInPerSecond')[0]
            st_oop=get_task_metrics_details(job_id, vid, tid+'.numRecordsOutPerSecond')[0]
            # metriclist.append({'id':'duration','value':vtask['duration']})
            # metriclist.append({'id':'read-bytes','value':vtask['metrics']['read-bytes']})
            # metriclist.append({'id':'write-bytes','value':vtask['metrics']['write-bytes']})
            # metriclist.append({'id':'read-records','value':vtask['metrics']['read-records']})
            # metriclist.append({'id':'write-records','value':vtask['metrics']['write-records']})
            if _DEBUG=='1':
                print(vid,'---------------------'+vname+'_'+tid+"\n", st_busytime, st_bkpstime, st_idletime, st_oip, st_oop)
            JobGraph.nodes[vid]['oip']+=str2int(st_oip['value'])
            JobGraph.nodes[vid]['oop']+=str2int(st_oop['value'])
            JobGraph.nodes[vid]['idletime']+=str2int(st_idletime['value'])
            JobGraph.nodes[vid]['bkpstime']+=str2int(st_bkpstime['value'])
            JobGraph.nodes[vid]['busytime']+=str2int(st_busytime['value'])
    toposeq=list(nx.topological_sort(JobGraph))    # topological_sort on operators
    print("topological_sort:    ", toposeq)
    for vid in toposeq:    # calc true input/output rate
        parallelism=JobGraph.nodes[vid]['parallelism']
        JobGraph.nodes[vid]['idletime']=JobGraph.nodes[vid]['idletime']/parallelism
        JobGraph.nodes[vid]['bkpstime']=JobGraph.nodes[vid]['bkpstime']/parallelism
        JobGraph.nodes[vid]['busytime']=JobGraph.nodes[vid]['busytime']/parallelism
        if JobGraph.nodes[vid]['busytime']<0:    # for source operators, busytime == NaN, true_rate == target_input_rate * source_parallelism
            JobGraph.nodes[vid]['tip']=0
            for src in srcratelist:
                srcname=list(src.keys())[0]
                if(srcname in JobGraph.nodes[vid]['name']):
                    JobGraph.nodes[vid]['top']=src[srcname]*parallelism
        else:
            if JobGraph.nodes[vid]['busytime']==0:
                JobGraph.nodes[vid]['busytime']=1    # avoid divide 0 error
            JobGraph.nodes[vid]['tip']=JobGraph.nodes[vid]['oip']/(JobGraph.nodes[vid]['busytime']/1000)
            JobGraph.nodes[vid]['top']=JobGraph.nodes[vid]['oop']/(JobGraph.nodes[vid]['busytime']/1000)
        if(JobGraph.nodes[vid]['oip']>0):
            JobGraph.nodes[vid]['selectivity']=JobGraph.nodes[vid]['oop']/JobGraph.nodes[vid]['oip']
    for vid in toposeq:    # calc optimal parallelism
        parallelism=JobGraph.nodes[vid]['parallelism']
        innodes=JobGraph.nodes[vid]['innodes']
        if(len(innodes)==0):
            JobGraph.nodes[vid]['optimalparallelism']=parallelism
        else:
            utop=0
            for uid in innodes:
                utop+=JobGraph.nodes[uid]['top']
            JobGraph.nodes[vid]['optimalparallelism']=(utop/JobGraph.nodes[vid]['tip'])*parallelism

    print("====================== logical dataflow ======================")
    for gn in JobGraph.nodes.items():
        print("node: ",gn)
    for ge in JobGraph.edges.items():
        print("edge: ", ge)
    time.sleep(60)
    clock-=60

