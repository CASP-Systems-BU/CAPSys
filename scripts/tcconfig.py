import sys, os

TCMD="/sbin/tc"

def runcmd(cmd):
    print('------------------------------------------------------------')
    print(cmd)
    res=os.popen(cmd).read()
    print(res)
    print('------------------------------------------------------------')
    return(res)

def createbandwidth(NIC, LIMIT):
    DST_CIDR="192.168.1.1/24"
    U32CMD=TCMD+" filter add dev "+NIC+" protocol ip parent 1:0 prio 1 u32"
    runcmd(TCMD+" qdisc add dev "+NIC+" root handle 1:0 htb default 30")
    runcmd(TCMD+" class add dev "+NIC+" parent 1:0 classid 1:1 htb rate "+LIMIT)
    runcmd(U32CMD+" match ip dst "+DST_CIDR+" flowid 1:1")

def createlatency(NIC, LIMIT):
    runcmd(TCMD+" qdisc add dev "+NIC+" root netem delay "+LIMIT)

def show(NIC):
    runcmd(TCMD+" qdisc show dev "+NIC)

def cleantc(NIC):
    runcmd(TCMD+" qdisc del dev "+NIC+" root")

# usage: python3 tcconfig.py create enp6s0f0 bandwidth 1000mbit
# usage: python3 tcconfig.py create enp6s0f0 latency 400ms
# usage: python3 tcconfig.py create enp6s0f0 unlimit
# usage: python3 tcconfig.py clean enp6s0f0

rcmd=sys.argv[1]
NIC=sys.argv[2]
if(rcmd=='create'):
    LTYPE=sys.argv[3]
    if(LTYPE=='unlimit'):
        print('createtc unlimit')
    if(LTYPE=='bandwidth'):
        LIMIT=sys.argv[4]
        createbandwidth(NIC, LIMIT)
    if(LTYPE=='latency'):
        LIMIT=sys.argv[4]
        createlatency(NIC, LIMIT)
else:
    cleantc(NIC)
