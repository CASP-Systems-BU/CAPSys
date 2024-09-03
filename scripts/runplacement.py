from exputils import *

resetsec=180
schedulercfg_list=[]

fjson=sys.argv[1]
tcmd=sys.argv[2]

cfg=json.loads(open(fjson,'r').read())
jarpath=cfg['jarpath']
jarargs=cfg['jarargs']
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


# Usage: python3 runplacement.py expjson/q5m_a.json restart
# just restart cluster
if(tcmd=='restart'):
    resetvpc(jmip, user, FLINKROOT, TMPROOT, SAVEROOT, ctype, iplist, resetsec, tcnic)
    exit()

# Usage: python3 runplacement.py expjson/q5m_a.json range 0 20
# run exp 0->20
if(tcmd=='range'):
    lts=int(sys.argv[3])
    rts=int(sys.argv[4])
    for i in range(lts,rts):
        schedulercfg_list.append("schedulercfg_"+str(i))

# Usage: python3 runplacement.py expjson/q5m_a.json select 0 1 2 3 4 5
# run selected exp
if(tcmd=='select'):
    lts=sys.argv[3:]
    for i in lts:
        schedulercfg_list.append("schedulercfg_"+str(i))

print(schedulercfg_list)
initjm(jmip, user, FLINKROOT, ctype, iplist)

sl=len(schedulercfg_list)
i=0
while(i<sl):
    try:
        scfg=schedulercfg_list[i]
        erootdir=str('../expresult/motiv/'+expname)
        edir=erootdir+'/exp_r'+str(retry)+'_'+scfg
        print(edir)
        resetvpc(jmip, user, FLINKROOT, TMPROOT, SAVEROOT, ctype, iplist, resetsec, tcnic)
        runcmd('mkdir '+erootdir)
        runcmd('mkdir '+edir)
        runcmd('scp ./'+erootdir+'/schedulercfg_list/'+scfg+' '+user+'@'+jmip+':'+FLINKROOT+'/scripts/schedulercfg')
        runcmd('ssh '+user+'@'+jmip+' "cd '+FLINKROOT+'/scripts/ ; python3 deployflink.py '+ctype+' start"')
        runsleep(30, 10)    # wait for deployment finishing

        rest_client = FlinkRestClient.get(host=jmip, port=jmpt)
        rest_client.overview()
        ur=upload_jar(jmip, jmpt, jarpath)
        jar_id = ur['filename'].split('/')[-1]
        job_id = rest_client.jars.run(jar_id, arguments=jarargs)
        job_id = rest_client.jobs.all()[0]['id']
        job = rest_client.jobs.get(job_id=job_id)
        print("deployed...")

        for ip in iplist:
            runcmd('ssh '+user+'@'+ip+' "cd '+FLINKROOT+'/scripts/ ; sudo python3 tcconfig.py create '+tcnic+' '+tclimit+'"')
        runsleep(10*60, 10)    # warmup 10min

        if(iolimit=="NONE"):
            print("no iolimit")
        else:
            for ip in iplist:
                runcmd('ssh '+user+'@'+ip+' "cd '+FLINKROOT+'/scripts/ ; ./iolimit.sh '+iolimit+' & "')
            print("running iolimit")

        tmidlist=[]
        for tm in rest_client.taskmanagers.all():
            tmidlist.append(tm['id'])

        print("starting...")
        clock=15*60    # run 15min
        while(clock>0):
            print("clock", clock, "-------------------------------------------------------------")
            vertex_ids=rest_client.jobs.get_vertex_ids(job_id)
            for vid in vertex_ids:
                jvurl="http://"+jmip+":"+str(jmpt)+"/jobs/"+job_id+"/vertices/"+vid
                res=requests.get(jvurl).json()
                #print(res)
                vts=str(res['now'])
                vname=res['name'].replace(' ','_').replace(',','_').replace(';','_')
                vpall=str(res['parallelism'])
                for tmid in tmidlist:
                    metriclist=[vts, vname, tmid]
                    metriclist.append(get_taskmanager_metrics_details(jmip, jmpt, tmid, "Status.Shuffle.Netty.AvailableMemorySegments"))
                    metriclist.append(get_taskmanager_metrics_details(jmip, jmpt, tmid, "Status.Shuffle.Netty.UsedMemorySegments"))
                    metriclist.append(get_taskmanager_metrics_details(jmip, jmpt, tmid, "Status.Shuffle.Netty.TotalMemorySegments"))
                    metriclist.append(get_taskmanager_metrics_details(jmip, jmpt, tmid, "Status.JVM.CPU.Time"))
                    metriclist.append(get_taskmanager_metrics_details(jmip, jmpt, tmid, "Status.JVM.CPU.Load"))
                    metriclist.append(get_taskmanager_metrics_details(jmip, jmpt, tmid, "Status.JVM.Threads.Count"))
                    ff=open(edir+'/'+tmid.replace(":","_"), 'a')
                    ffstring=""
                    for mtc in metriclist:
                        ffstring+=str(mtc)
                        ffstring+='; '
                    ff.write(ffstring+'\n')
                for vtask in res['subtasks']:
                    ttm=vtask['taskmanager-id']
                    tid=str(vtask['subtask'])
                    metriclist=[vts, vname, vpall, ttm, tid]
                    metriclist.append(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.busyTimeMsPerSecond'))
                    metriclist.append(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.backPressuredTimeMsPerSecond'))
                    metriclist.append(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.idleTimeMsPerSecond'))
                    metriclist.append(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.numRecordsInPerSecond'))
                    metriclist.append(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.numRecordsOutPerSecond'))
                    metriclist.append(str([{'id':'duration','value':vtask['duration']}]))
                    metriclist.append(str([{'id':'read-bytes','value':vtask['metrics']['read-bytes']}]))
                    metriclist.append(str([{'id':'write-bytes','value':vtask['metrics']['write-bytes']}]))
                    metriclist.append(str([{'id':'read-records','value':vtask['metrics']['read-records']}]))
                    metriclist.append(str([{'id':'write-records','value':vtask['metrics']['write-records']}]))
                    metriclist.append(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.'+vname+'.rocksdb_bytes_read'))
                    metriclist.append(get_task_metrics_details(jmip, jmpt, job_id, vid, tid+'.'+vname+'.rocksdb_bytes_written'))

                    #print(vts, vname, vpall, ttm, tid, t_busytime, t_backpressure, t_idletime, t_opsin, t_opsout)
                    ff=open(edir+'/'+vname+'_'+tid, 'a')
                    ffstring=""
                    for mtc in metriclist:
                        ffstring+=str(mtc)
                        ffstring+='; '
                    ff.write(ffstring+'\n')
            time.sleep(5)
            clock-=5

        logurl=[]
        for tm in tmidlist:
            for ll in rest_client.taskmanagers.get_logs(tm):
                ln=ll['name']
                if(ln.endswith('.log')):
                    print(tm, ln)
                    logurl.append("http://"+jmip+":"+str(jmpt)+"/taskmanagers/"+tm+"/logs/"+ln)
                    # http://192.168.1.105:8081/taskmanagers/192.168.1.153:38019-96b53d/logs/flink-tidb-taskexecutor-0-flink3.log

        print(logurl)
        for lg in logurl:
            runcmd('wget -P ./'+edir+' '+lg)

        print('successfully run ',scfg)
        i+=1
        retry=5
    except Exception as ex:
        print(ex)
        print('failed. will retry ',scfg,' for ',retry,' times')
        retry-=1
        if(retry<0):
            i+=1
            retry=5
        continue
    resettc(user, iplist, tcnic, FLINKROOT)
