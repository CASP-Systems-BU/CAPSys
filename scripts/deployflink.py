import sys,os


# python3 deployflink.py aws start
dloc=sys.argv[1]
dcmd=sys.argv[2]


def stopflink(dloc):
    FLINKROOT=os.path.dirname(os.getcwd())  # .../flink-placement-16
    CFGROOT=FLINKROOT+"/scripts/"+dloc
    print(CFGROOT)

    print(os.popen("cp "+CFGROOT+"/* "+FLINKROOT+"/flink-dist/target/flink-1.16.2-bin/flink-1.16.2/conf/").read())
    print("stopping flink...    "+CFGROOT)
    print(os.popen("cd "+FLINKROOT+"/flink-dist/target/flink-1.16.2-bin/flink-1.16.2/bin/ ; ./stop-cluster.sh").read())
    print(os.popen("rm "+FLINKROOT+"/flink-dist/target/flink-1.16.2-bin/flink-1.16.2/log/*").read())
    print("stopped flink")


def startflink(dloc):
    FLINKROOT=os.path.dirname(os.getcwd())  # .../flink-placement-16
    CFGROOT=FLINKROOT+"/scripts/"+dloc
    TMPROOT=os.path.dirname(FLINKROOT)+"/tmp/"  # .../tmp
    print(CFGROOT)

    localip=os.popen("hostname -I").read()+" 127.0.0.1"
    print(localip)
    iplist=[]
    print("starting flink...     "+CFGROOT)
    print(os.popen("cd "+CFGROOT).read())

    for ip in open(CFGROOT+"/workers",'r').readlines():
        iplist.append(ip.replace("\n",""))
    for ip in open(CFGROOT+"/masters",'r').readlines():
        iplist.append(ip.replace("\n","").replace(':8081',''))

    for ip in iplist:
        print(os.popen("cp "+CFGROOT+"/flink-conf.yaml "+CFGROOT+"/flink-conf.yaml"+ip.replace('.','')).read())
        ff=open(CFGROOT+"/flink-conf.yaml"+ip.replace('.',''), 'r').read().replace('WORKERIP',ip)
        wf=open(CFGROOT+"/flink-conf.yaml"+ip.replace('.',''), 'w').write(ff)

    print(os.popen("cp "+CFGROOT+"/* "+FLINKROOT+"/flink-dist/target/flink-1.16.2-bin/flink-1.16.2/conf/").read())

    print(os.popen('rm -rf /tmp/flink*').read())
    for ip in iplist:
        if not (ip in localip):
            print('-----------------------------------------------------')
            print(ip)
            print(os.popen('ssh '+ip+' "rm -rf ~/.javacpp "').read())
            print(os.popen('ssh '+ip+' "rm -rf '+TMPROOT+'/*"').read())
            print(os.popen('ssh '+ip+' "rm -rf '+FLINKROOT+'/flink-dist/target"').read())
            print(os.popen('ssh '+ip+' "mkdir '+FLINKROOT+'/"').read())
            print(os.popen('ssh '+ip+' "mkdir '+FLINKROOT+'/scripts/"').read())
            print(os.popen('ssh '+ip+' "mkdir '+FLINKROOT+'/flink-dist"').read())
            print(os.popen('ssh '+ip+' "mkdir '+FLINKROOT+'/flink-dist/target"').read())
            print(os.popen('scp -r '+FLINKROOT+'/flink-dist/target/flink-1.16.2-bin/ '+ip+':'+FLINKROOT+'/flink-dist/target/').read())

    for ip in iplist:
        print(ip)
        print(os.popen('ssh '+ip+' "cd '+FLINKROOT+'/flink-dist/target/flink-1.16.2-bin/flink-1.16.2/conf ; mv flink-conf.yaml'+ip.replace('.','')+' flink-conf.yaml"').read())
        print(os.popen('ssh '+ip+' "cp '+FLINKROOT+'/flink-dist/target/flink-1.16.2-bin/flink-1.16.2/conf/flink-conf.yaml '+FLINKROOT+'/scripts/flink-conf.yaml"').read())    # customscheduler need to read it

    for ip in iplist:
        print(os.popen("rm "+CFGROOT+"/flink-conf.yaml"+ip.replace('.','')).read())

    print('-----------------------------------------------------')
    print(os.popen('cd '+FLINKROOT+'/flink-dist/target/flink-1.16.2-bin/flink-1.16.2/bin ; ./start-cluster.sh').read())
    print("started flink")


stopflink(dloc)
if(dcmd=='start'):
    startflink(dloc)


