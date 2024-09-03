## Instructions for setting up evaluation environment on AWS

This document assuming we have created a AWS EC2 cluster with 5 nodes:
```
JobManager    192.168.1.6
TaskManager1    192.168.1.101
TaskManager2    192.168.1.102
TaskManager3    192.168.1.103
TaskManager4    192.168.1.104
```

### 1. Format disk and setup working directory.  (on every node)

After initializing EC2 instances, use `sudo fdisk -l` to check the ID of EBS disk (Disk model: Amazon Elastic Block Store) and SSD disk (Disk model: Amazon EC2 NVMe Instance Storage). 
Here we assume `/dev/nvme0n1` is EBS disk and `/dev/nvme1n1` is SSD disk. By default the system is installed on EBS disk, and Flink environment (including temp dir) should be under SSD disk.

use the following commands to format disk and setup working directory:

```
mkdir ~/data
mkdir ~/dataebs
sudo umount /dev/nvme1n1
sudo mkfs.ext4 /dev/nvme1n1 -F
sudo mount -t ext4 /dev/nvme1n1 ~/data -o defaults,nodelalloc,noatime
sudo chmod o+w ~/data
sudo chown ubuntu ~/data
df -h
```



### 2. Install necessary libraries.  (on every node)

```
sudo apt update
sudo apt install openjdk-11-jdk-headless iperf iperf3 htop git python3-pip unzip net-tools p7zip-full nload iotop iftop chrony cifs-utils samba nvme-cli nfs-kernel-server nfs-common -y
sudo pip3 install flink_rest_client networkx pandas numpy

# setup maven
sudo rm /usr/bin/mvn*
wget https://dlcdn.apache.org/maven/maven-3/3.8.8/binaries/apache-maven-3.8.8-bin.zip
unzip apache-maven-3.8.8-bin.zip
sudo ln -s ~/apache-maven-3.8.8/bin/mvnDebug /usr/bin/mvnDebug
sudo ln -s ~/apache-maven-3.8.8/bin/mvnyjp  /usr/bin/mvnyjp
sudo ln -s ~/apache-maven-3.8.8/bin/mvn  /usr/bin/mvn

# setup golang
wget https://go.dev/dl/go1.22.2.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.22.2.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
source ~/.profile
go version
```

### 3. Setup ssh key on Job manager  (on every node)

**on jobmanager** , get public key of jobmanager
```
ssh-keygen
cat ~/.ssh/id_rsa.pub
```

Then add the public key of **jobmanager** to all ndoes (including jobmanager itself)
```
echo [public key] >> ~/.ssh/authorized_keys
```

### 4. Set up Prometheus on all nodes  (on every node)

Although our work didn't use TiDB, we use the Prometheus dashboard intergrated with TiDB to collect CPU metrics in the cluster.

```
curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh
source /home/ubuntu/.bashrc
```

### 5. setup NFS on jobmanager  (on jobmanager)

NFS is used to store job savepoints for reconfiguration purpose. 

**5.1 Create shared folder**

```
mkdir /home/ubuntu/data/savepoint
```

**5.2 Edit config file**

```
sudo vi /etc/exports
```
Append the following line to /etc/exports
```
/home/ubuntu/data/savepoint 192.168.1.0/24(rw,sync,no_subtree_check)
```

**5.3. Apply the configuration**
```
sudo exportfs -a
```

**5.4. Start and enable the NFS server**
```
sudo systemctl restart nfs-kernel-server
sudo systemctl enable nfs-kernel-server
```

Show NFS server mount status
```
showmount -e 192.168.1.6
```

### 6. Compile Flink and Queries  (on jobmanager)

```
cd ~/data/
git clone git@github.com:CASP-Systems-BU/CAPSys.git ~/data/flink-placement-16/

#Compile Flink
cd ~/data/flink-placement-16/scripts
./makeflink.sh

#Compile Queries
cd ~/data/flink-placement-16/queries/nexmark/
mvn clean package
cd ~/data/flink-placement-16/queries/deem22/
mvn clean package
cp -r ~/data/flink-placement-16/queries/deem22/models/ ~/data/
```

We also prepared a script for automatically mount disk and start prometheus everytime after restart.  
```
cp ~/data/flink-placement-16/scripts/aws/ec2tools.py ~/
```

### 7. copy Flink binary and queries to all nodes  (on jobmanager)

```
ssh 192.168.1.101 "mkdir ~/data/flink-placement-16/"
ssh 192.168.1.102 "mkdir ~/data/flink-placement-16/"
ssh 192.168.1.103 "mkdir ~/data/flink-placement-16/"
ssh 192.168.1.104 "mkdir ~/data/flink-placement-16/"

scp -r ~/data/flink-placement-16/{scripts,queries,flink-dist,flink-dstl} 192.168.1.101:~/data/flink-placement-16/
scp -r ~/data/flink-placement-16/{scripts,queries,flink-dist,flink-dstl} 192.168.1.102:~/data/flink-placement-16/
scp -r ~/data/flink-placement-16/{scripts,queries,flink-dist,flink-dstl} 192.168.1.103:~/data/flink-placement-16/
scp -r ~/data/flink-placement-16/{scripts,queries,flink-dist,flink-dstl} 192.168.1.104:~/data/flink-placement-16/


scp -r ~/data/models/ 192.168.1.101:~/data/
scp -r ~/data/models/ 192.168.1.102:~/data/
scp -r ~/data/models/ 192.168.1.103:~/data/
scp -r ~/data/models/ 192.168.1.104:~/data/

scp -r ~/ec2tools.py 192.168.1.101:~/
scp -r ~/ec2tools.py 192.168.1.102:~/
scp -r ~/ec2tools.py 192.168.1.103:~/
scp -r ~/ec2tools.py 192.168.1.104:~/
```

### 8. start Prometheus cluster (on jobmanager)

```
cd ~/data/flink-placement-16/scripts/aws
tiup cluster deploy tidb-test v6.5.0 tidbtopo.yaml
tiup cluster start tidb-test --init
```
