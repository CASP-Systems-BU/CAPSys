from flink_rest_client import FlinkRestClient
import sys, os, time, json, requests, json, math, time, pickle
import networkx as nx
import numpy as np
import pandas as pd
from collections import defaultdict
from datetime import datetime
retry=5

def gettimestamp():
    return(str(int(time.time())))

def nested_dict():
    return defaultdict(int)

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
    print(res)
    print('------------------------------------------------------------')
    return(res)

def get_task_vertix_metrics(jmip, jmpt, job_id, vid):
    url="http://"+jmip+":"+str(jmpt)+"/jobs/"+job_id+"/vertices/"+vid+"/metrics"
    response = requests.get(url)
    response.raise_for_status()
    ans=response.json()
    return(ans)

def get_task_vertix_details(jmip, jmpt, job_id, vid):
    url="http://"+jmip+":"+str(jmpt)+"/jobs/"+job_id+"/vertices/"+vid
    response = requests.get(url)
    response.raise_for_status()
    ans=response.json()
    return(ans)

def get_task_metrics_details(jmip, jmpt, jobid, vid, fieldid):
    _metriclist = get_task_vertix_metrics(jmip, jmpt, jobid, vid)
    metriclist = [d['id'] for d in _metriclist]
    if(not (fieldid in metriclist)):
        return([{"id":fieldid, "value":0}])
    # http://192.168.1.105:8081/jobs/e81ee095a99bfc431e260d044ff7e03d/vertices/ea632d67b7d595e5b851708ae9ad79d6/metrics?get=4.busyTimeMsPerSecond
    url = "http://"+jmip+":"+str(jmpt)+"/jobs/{}/vertices/{}/metrics?get={}".format(jobid, vid, fieldid)
    response = requests.get(url)
    response.raise_for_status()
    ans=response.json()#[0]['value']
    return(ans)

def get_job_plan_details(jmip, jmpt, jobid):
    # http://192.168.1.105:8081/jobs/e81ee095a99bfc431e260d044ff7e03d/plan
    url = "http://"+jmip+":"+str(jmpt)+"/jobs/{}/plan".format(jobid)
    response = requests.get(url)
    response.raise_for_status()
    ans=response.json()#[0]['value']
    return(ans)

def get_taskmanager_metrics_details(jmip, jmpt, tmid, fieldid):
    # http://192.168.1.180:8081/taskmanagers/192.168.1.181:43893-b21053/metrics
    url = "http://"+jmip+":"+str(jmpt)+"/taskmanagers/{}/metrics?get={}".format(tmid, fieldid)
    response = requests.get(url)
    response.raise_for_status()
    ans=response.json()#[0]['value']
    return(ans)

def upload_jar(jmip, jmpt, jarpath):
    fname=jarpath.split('/')[-1]
    print(fname)
    jfile = {"file": (fname, (open(jarpath, "rb")), "application/x-java-archive")}
    url="http://"+jmip+":"+str(jmpt)+"/jars/upload"
    response = requests.request(method="POST", url=url, files=jfile)
    return(response.json())

def resettc(user, iplist, tcnic, FLINKROOT):
    for ip in iplist:
        runcmd('ssh '+user+'@'+ip+' "cd '+FLINKROOT+'/scripts/ ; sudo python3 tcconfig.py clean '+tcnic+'"')

def resetvpc(jmip, user, FLINKROOT, TMPROOT, SAVEROOT, ctype, iplist, resetsec, tcnic):
    for ip in iplist:
        runcmd('ssh '+user+'@'+ip+' "cd '+FLINKROOT+'/scripts/ ; sudo python3 tcconfig.py clean '+tcnic+'"')
    runcmd('ssh '+user+'@'+jmip+' "cd '+FLINKROOT+'/scripts/ ; python3 deployflink.py '+ctype+' stop"')
    for ip in iplist:
        runcmd('ssh '+user+'@'+ip+' "sudo reboot"')
    runsleep(resetsec, 10)
    runcmd('cd ~/; python3 ec2tools.py mountall')
    for ip in iplist:
        runcmd('ssh '+user+'@'+ip+' "rm -rf '+TMPROOT+' ; mkdir '+TMPROOT+' "')
        runcmd('ssh '+user+'@'+ip+' "mkdir '+TMPROOT+'/flinkstate"')
        runcmd('ssh '+user+'@'+ip+' "mkdir '+SAVEROOT+'"')
        if(SAVEROOT!=""):
            runcmd('ssh '+user+'@'+ip+' "sudo mount -t cifs -o rw,guest,vers=3.0,uid='+user+',gid='+user+' //'+jmip+'/savepoint '+SAVEROOT+'"')
        #runcmd('ssh '+user+'@'+ip+' "sudo systemctl restart systemd-timesyncd.service"')
        # sudo systemctl status systemd-timesyncd.service

def initjm(jmip, user, FLINKROOT, ctype, iplist):
    runcmd('ssh '+user+'@'+jmip+' "mkdir '+FLINKROOT+'"')
    runcmd('scp -r ../scripts'+' '+user+'@'+jmip+':'+FLINKROOT+'/')
    runcmd('scp -r ../flink-dist'+' '+user+'@'+jmip+':'+FLINKROOT+'/')
    for ip in iplist:
        runcmd('ssh '+user+'@'+ip+' "mkdir '+FLINKROOT+'"')
        runcmd('scp -r ../scripts'+' '+user+'@'+ip+':'+FLINKROOT+'/')

def startjob(jmip, jmpt, user, FLINKROOT, TMPROOT, SAVEROOT, iplist, resetsec, ctype, jarpath, jarargs, tcnic, tclimit, fromsavepoint):
    initjm(jmip, user, FLINKROOT, ctype, iplist)
    resetvpc(jmip, user, FLINKROOT, TMPROOT, SAVEROOT, ctype, iplist, resetsec, tcnic)
    runcmd('ssh '+user+'@'+jmip+' "cd '+FLINKROOT+'/scripts/ ; python3 deployflink.py '+ctype+' start"')
    runsleep(30, 10)    # wait for deployment finishing
    rest_client = FlinkRestClient.get(host=jmip, port=jmpt)
    rest_client.overview()
    ur=upload_jar(jmip, jmpt, jarpath)
    jar_id = ur['filename'].split('/')[-1]
    savepath=""
    if(SAVEROOT!=""):
        saveroot = os.listdir(SAVEROOT)
        savepoint_dir= [x for x in saveroot if os.path.isdir(os.path.join(SAVEROOT, x))]
        if(len(savepoint_dir)>0 and fromsavepoint):    # have at least 1 savepoint
            savepath = os.path.join(SAVEROOT, savepoint_dir[0])
    if(savepath!=""):
        job_id = rest_client.jars.run(jar_id, arguments=jarargs, savepoint_path=savepath)
    else:
        job_id = rest_client.jars.run(jar_id, arguments=jarargs)
    runsleep(30, 10)    # run job for a while before recording
    print("deployed...")
    runtclimit(user, FLINKROOT, iplist, tcnic, tclimit)
    return(job_id)

def runtclimit(user, FLINKROOT, iplist, tcnic, tclimit):
    for ip in iplist:
        runcmd('ssh '+user+'@'+ip+' "cd '+FLINKROOT+'/scripts/ ; sudo python3 tcconfig.py create '+tcnic+' '+tclimit+'"')
    print("runtclimit")
    runsleep(30, 10)    # run job for a while before recording

def redeploy(schedulercfg, oprlist):
    pass
    # TODO: redeploy with diff placement/parallelism

def createJobSavepoint(user, jmip, jmpt, job_id, SAVEROOT):
    runcmd('ssh '+user+'@'+jmip+' "rm -r '+SAVEROOT+'/* "')
    print("creating savepoint...")
    rest_client = FlinkRestClient.get(host=jmip, port=jmpt)
    rest_client.overview()
    res=rest_client.jobs.create_savepoint(job_id, SAVEROOT)
    runsleep(120, 30)    # need time to create savepoint
    print(res.status)

def getFlinkLogLatency(fpath, skipsec):
    # read latency
    latencyvalist=[]
    minlt=9999999999999
    maxlt=0
    ff=open(fpath, 'r').readlines()
    fcnt=0
    _starttimestamp=ff[0].split(',')[0]
    starttimestamp=datetime.strptime(_starttimestamp, '%Y-%m-%d %H:%M:%S')
    for _ll, _lc in enumerate(ff):
        if(('%latency%' in _lc)and(not 'latencyFromOperator' in _lc)):
            _ltimestamp=_lc.split(',')[0]
            ltimestamp=datetime.strptime(_ltimestamp, '%Y-%m-%d %H:%M:%S')
            duration=(ltimestamp-starttimestamp).total_seconds()
            if(duration>=skipsec):                            # ignore first several sec
                ll=_lc.split('%latency%')[1].split('%')[0]
                lt=_lc.split('%latency%')[1].split('%')[1]
                latencyvalist.append((int(lt), int(ll)))
                minlt=min(int(lt), minlt)
                maxlt=max(int(lt), maxlt)
                fcnt+=1
    print(fpath,fcnt, len(latencyvalist))
    return(latencyvalist)
#     if(len(latencyvalist)>0):
#         latencyvalist.sort()
#         nvalist=np.array(latencyvalist)
#         # print("  latency_avg", np.average(nvalist[:,1]))
#         # print('  latency_p99', np.percentile(nvalist[:,1], 99))
#         return(( np.average(nvalist[:,1]) , np.percentile(nvalist[:,1], 99) ))
#     return((-1, -1))    # this log file does not contain latency counter

def getFlinkLogPlacement(fpath):
    res=[]
    kwd='switched from INITIALIZING to RUNNING'
    ff=open(fpath, 'r').readlines()
    for _ll, _lc in enumerate(ff):
        if(kwd in _lc):
            opr=_lc.split("[] - ")[1].replace(kwd, "").replace("\n", "")
            res.append(opr)
    return(res)
