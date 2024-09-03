import os, sys, copy
import logging

'''
generate schedulercfg* file for all possible placement plans
Usage: python3 permutation.py q5m_c
'''

ts=sys.argv[1]
if(ts.startswith('q5m')):
    rate=7300*2
    numtasks={    # Query 5-MOD
        0: {'name': 'Source', 'parallelism': 2, 'state': 0, 'compute': 0.01517897065399*rate/2, 'vid': 0},
        1: {'name': 'Transform', 'parallelism': 5, 'state': 0, 'compute': 0.0194826611383339*rate/5, 'vid': 1},
        2: {'name': 'SlidingWindow', 'parallelism': 8, 'state': 1304920.709, 'compute': 0.513418245053344*rate/8, 'vid': 2},
        3: {'name': 'Sink', 'parallelism': 1, 'state': 0, 'compute': 0.00410162052343577*rate*2.5/1, 'vid': 3}  # window selectivity=2.5
    }
    edgelist={
        (0, 1): {'traffic': 97.17908832042920, 'rate': rate},
        (1, 2): {'traffic': 150.3935874481710, 'rate': rate},
        (2, 3): {'traffic': 41.14048438263730, 'rate': rate*2.5}
    }
elif(ts.startswith('deem')):
    rate=550*3
    numtasks={    # deem tuned, 766 plans
        0: {'name': 'Source', 'parallelism': 3, 'state': 0, 'compute': 0.99*rate/3, 'vid': 0},
        1: {'name': 'Transform', 'parallelism': 5, 'state': 0, 'compute': 2.07*rate/5, 'vid': 1},
        2: {'name': 'Compress', 'parallelism': 3, 'state': 0, 'compute': 1.11*rate/3, 'vid': 2},
        3: {'name': 'Inference', 'parallelism': 4, 'state': 0, 'compute': 1.23*rate/4, 'vid': 3},
        4: {'name': 'Sink', 'parallelism': 1, 'state': 0, 'compute': 0.04*rate/1, 'vid': 4}
    }
    edgelist={
        (0, 1): {'traffic': 80.1, 'rate': rate},      # KB per record
        (1, 2): {'traffic': 80.1, 'rate': rate},
        (2, 3): {'traffic': 3.85, 'rate': rate},
        (3, 4): {'traffic': 0.11, 'rate': rate}
    }
elif(ts.startswith('q8m')):
    numtasks={    # Query 8-MOD, 950 plans
        0: {'name': 'SourcePersons', 'parallelism': 1, 'state': 0, 'compute': 0, 'vid': 0},
        1: {'name': 'SourceAuctions', 'parallelism': 2, 'state': 0, 'compute': 0, 'vid': 1},
        2: {'name': 'TransformPersons', 'parallelism': 1, 'state': 0, 'compute': 0, 'vid': 2},
        3: {'name': 'TransformAuctions', 'parallelism': 4, 'state': 0, 'compute': 0, 'vid': 3},
        4: {'name': 'TumblingEventTimeWindows', 'parallelism': 7, 'state': 1, 'compute': 0, 'vid': 4},
        5: {'name': 'DummyLatencySink', 'parallelism': 1, 'state': 0, 'compute': 0, 'vid': 5}
    }
    edgelist={
        (0, 2): {'traffic': 0.22},
        (1, 3): {'traffic': 0.49},
        (2, 4): {'traffic': 1.09},
        (3, 4): {'traffic': 1.1},
        (4, 5): {'traffic': 0.04}
    }

workers_ip=['192.168.1.8', '192.168.1.9', '192.168.1.12', '192.168.1.13']
# workers_ip=['192.168.1.180', '192.168.1.181', '192.168.1.182']
workers_slot=4
totslot=len(workers_ip)*workers_slot
tottask=0
for tv in numtasks:
    tottask+=numtasks[tv]['parallelism']
if(totslot-tottask>0):      # 'None' means empty slots if total num of tasks < total num of slots
    numtasks[-1]={'name': 'None', 'parallelism': totslot-tottask, 'state': 0, 'compute': 0, 'vid': -1}

walked=set()
allocate=['None' for x in range(totslot)]

def runcmd(cmd):
    print('------------------------------------------------------------')
    print(cmd)
    res=os.popen(cmd).read()
    print('------------------------------------------------------------')
    return(res)

def allocate2set(allocate):
	res=[]
	for i in range(len(workers_ip)):
		ww=[]
		for j in range(workers_slot):
			idx=i*workers_slot+j
			ww.append(allocate[idx])
		ww.sort()
		res.append(tuple(ww))
	res.sort()
	return(tuple(res))

def dfs(allocate, x):
	if(x==totslot):
		walked.add(allocate2set(allocate))
# 		if(len(walked)%100==0):
# 		    print("len(walked)", len(walked))
	else:
		for tv in numtasks.keys():
			if(numtasks[tv]['parallelism']>=1):
				allocate[x]=tv
				numtasks[tv]['parallelism']-=1
				dfs(allocate, x+1)
				numtasks[tv]['parallelism']+=1

def printcfg(wx, fname):
    ff=open(fname, 'w')
    tmp=copy.deepcopy(numtasks)
    for i in range(len(workers_ip)):
        tsklist=list(wx[i])
        for j in range(len(tsklist)):
            tskno=tsklist[j]
            subtskid='('+str(tmp[tskno]['parallelism'])+'/'+str(numtasks[tskno]['parallelism'])+')'
            tmp[tskno]['parallelism']-=1
            tskname=tmp[tskno]['name']
            #tskname=tskname+' '+subtskid        # dont need write subtask id now
            if(tskno!=-1):
                ff.write(tskname+'; '+workers_ip[i]+'\n')
                print(tskname+'; '+workers_ip[i])
    ff.close()

def scoring(wx):
    # calc score based on heuristics
    nw=len(wx)             # num of workers
    ns=len(wx[0])          # num of slots per worker
    alinks=0               # total number of virtual links
    astate=0               # total resource usage on state
    acomp=0                # total resource usage on compute
    atraffic=0             # total resource usage on network
    worsttraffc=0          # largest traffic of one worker under worst placement
    atrafficlist=[]
    for (vi, vj) in edgelist:
        pi=numtasks[vi]['parallelism']
        pj=numtasks[vj]['parallelism']
        if(pi!=pj):
            alinks += (pi*pj)
        else:
            alinks += pi
        atraffic += edgelist[(vi, vj)]['traffic']*edgelist[(vi, vj)]['rate']
        atrafficlist.append(edgelist[(vi, vj)]['traffic']*edgelist[(vi, vj)]['rate'])
    clinks=0      # num of remote virtual links
    wlinks=0      # sum(weight*clink)
    tcpch=0       # num of TCP channels
    ccomp=0       # max co-locate degree of compute per node
    cstate=0      # max co-locate degree of state per node
    otraffic=0    # max outbound traffic per node
    atrafficlist=sorted(atrafficlist)
    worsttraffc=sum(atrafficlist[-workers_slot:])
    for i in range(0,nw):
        _otraffic=0
        for j in range(0,nw):
            if(j!=i):
                tcps=set()
                tsklist_i=list(wx[i])
                tsklist_j=list(wx[j])
                for ti in tsklist_i:
                    for tj in tsklist_j:
                        if ((ti, tj) in edgelist):
                            pi=numtasks[ti]['parallelism']
                            pj=numtasks[tj]['parallelism']
                            print("_otraffic", ti, tj, edgelist[(ti, tj)]['traffic'], edgelist[(ti, tj)]['rate'], (pi*pj))
                            _otraffic+=edgelist[(ti, tj)]['traffic']*edgelist[(ti, tj)]['rate']/(pi*pj)    # outbound traffic from node i
                            clinks+=1
                            wlinks+=edgelist[(ti, tj)]['traffic']*edgelist[(ti, tj)]['rate']/(pi*pj)
                            tcps.add((ti, tj))
                #print("tcps ", tcps, len(tcps))
                tcpch+=len(tcps)
        otraffic=max(otraffic, _otraffic)
    for i in range(0,nw):
        _cstate=0
        _ccomp=0
        tsklist=list(wx[i])    # all tasks in worker i
        for tt in tsklist:
            if(numtasks[tt]['state']!=0):
                _cstate+=numtasks[tt]['state']
            if(numtasks[tt]['compute']!=0):
                _ccomp+=numtasks[tt]['compute']
        astate += _cstate
        acomp += _ccomp
        cstate=max(cstate, _cstate)
        ccomp=max(ccomp, _ccomp)
    scoringres={'ccomp': ccomp, 'acomp': acomp, 'hcomp': 0 if acomp==0 else ccomp/(acomp/nw),
                'cstate': cstate, 'astate': astate,'hstate': 0 if astate==0 else cstate/(astate/nw),
                'otraffic': otraffic, 'atraffic': atraffic, 'htraffic': 0 if atraffic==0 else otraffic/worsttraffc, # otraffic/(atraffic/nw),
                'clinks': clinks, 'wlinks': wlinks, 'tcpch': tcpch, 'alinks': alinks,
                'nw': nw, 'ns': ns}
    return(scoringres)

if __name__ == "__main__":
    print(totslot,'slots in total: ',len(workers_ip),' workers * ',workers_slot,' slots')
    cnt=0
    dfs(allocate, 0)
    print(len(walked))
    erootdir='../expresult/'+str(ts)
    edir=erootdir+'/schedulercfg_list'
    print(edir)
    runcmd('mkdir '+erootdir)
    runcmd('mkdir '+edir)
    lwalked=[]
    for wx in walked:
        scoringres = scoring(wx)
        sx=(scoringres['clinks']/scoringres['alinks'])+(scoringres['cstate']/scoringres['ns'])
        scoringres['plan']=wx
        scoringres['score']=sx
        lwalked.append(scoringres)
    lwalked=sorted(lwalked, key=lambda x:x['score'])
    for dwx in lwalked:
        print(cnt,'---------------------------------')
        wx=dwx['plan']
        print(wx, dwx)
        printcfg(wx, edir+'/schedulercfg_'+str(cnt))
        cnt+=1
    print(cnt, len(lwalked))
