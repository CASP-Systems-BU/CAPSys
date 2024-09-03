import sys, os, re

iplist=["192.168.1.101",
        "192.168.1.102",
        "192.168.1.103",
        "192.168.1.104",
        "192.168.1.105",
        "192.168.1.106",
        "192.168.1.107",
        "192.168.1.108",
        "192.168.1.109",
        "192.168.1.110",
        "192.168.1.111",
        "192.168.1.112",
        "192.168.1.113",
        "192.168.1.114",
        "192.168.1.115",
        "192.168.1.116",
        "192.168.1.117",
        "192.168.1.118",
        "192.168.1.119",
        "192.168.1.120",
        "192.168.1.6"]

# Helper function

def runcmd(cmd, pcmd=True):
    print('------------------------------------------------------------')
    print(cmd)
    res=os.popen(cmd).read()
    # if error, res is empty string
    if(pcmd):
        print(res)
    print('------------------------------------------------------------')
    return(res)

def getNvmeId(ip):
    nvmelist=re.findall(r'nvme\d+n\d+', runcmd('ssh '+ip+' ls /dev/nvme*', pcmd=False))
    for ndev in nvmelist:
        res=runcmd('ssh '+ip+' "sudo nvme id-ctrl -v /dev/'+ndev+'  | grep mn"', pcmd=False)
        if "Amazon EC2 NVMe Instance Storage" in res:
            return(ndev)

# Check if worker is running
def nodeDown(ip):
    res = runcmd('ssh '+ip+' pwd', pcmd=False)
    return res == ''

# Check if the destination folder is empty
def folderEmpty(ip, folder):
    res = runcmd('ssh '+ip+' ls ~/'+folder, pcmd=False)
    return res == '' or res == 'lost+found\n'

# Interface

def mountall():
    for ip in iplist:
        print(ip)
        if nodeDown(ip):
            print(f"Node {ip} is down --> skip")
            continue
        nvmeid=getNvmeId(ip)
        runcmd('ssh '+ip+' "sudo mount -t ext4 /dev/'+nvmeid+' ~/data -o defaults,nodelalloc,noatime"')
        runcmd('ssh '+ip+' "mkdir ~/data/tmp"')

def backup(targetIP=None):
    global iplist
    if not targetIP == None:
        iplist = [targetIP]
    else:
        print("Before backup all nodes: shut down the Flink cluster")
        runcmd('cd ~/data/flink-placement-16/scripts/ ; python3 deployflink.py aws stop')
    for ip in iplist:
        print(ip)
        if nodeDown(ip):
            print(f"Node {ip} is down --> skip")
            continue
        if not folderEmpty(ip, "dataebs"):
            print(f"ERROR: Node {ip} ~/dataebs folder is not empty: need backup this node manually!")
            continue
        if not ip == "192.168.1.6":
            runcmd('ssh '+ip+' "sudo umount ~/data/savepoint"')
            runcmd('ssh '+ip+' "rm -rf ~/data/savepoint"')
        runcmd('ssh '+ip+' "mv ~/data/* ~/dataebs/"')

def restore(targetIP=None):
    global iplist
    if not targetIP == None:
        iplist = [targetIP]
    for ip in iplist:
        print(ip)
        if nodeDown(ip):
            print(f"Node {ip} is down --> skip")
            continue
        # skip node that is already restored
        if folderEmpty(ip, "dataebs"):
            print(f"ERROR: Node {ip} ~/dataebs folder is empty: no restore() on this node")
            continue
        nvmeid=getNvmeId(ip)
        runcmd('ssh '+ip+' "sudo umount /dev/'+nvmeid+'  ;  sudo mkfs.ext4 /dev/'+nvmeid+' -F  ;  sudo mount -t ext4 /dev/'+nvmeid+' ~/data -o defaults,nodelalloc,noatime  ;  sudo chmod o+w ~/data  ;  sudo chown ubuntu ~/data"')
        runcmd('ssh '+ip+' "mv ~/dataebs/* ~/data/"')

def diskstat():
    for ip in iplist:
        print(ip)
        if nodeDown(ip):
            print(f"Node {ip} is down --> skip")
            continue
        runcmd('ssh '+ip+' "df -h"')

numcmd = len(sys.argv)
_CMD=sys.argv[1]
if(_CMD=='mountall'):
    mountall()
elif(_CMD=='backup'):
    if numcmd == 2:
        backup()
    elif numcmd == 3:
        backup(sys.argv[2])
elif(_CMD=='restore'):
    if numcmd == 2:
        restore()
    elif numcmd == 3:
        restore(sys.argv[2])
elif(_CMD=='diskstat'):
    diskstat()
