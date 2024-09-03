#!/bin/bash
export FLINKROOT=$(builtin cd ..; pwd)
echo $FLINKROOT

localip=$(hostname -I)
#localip=${$localip//\n/}

printf '%s\n' $localip

iplist=()

cp "$FLINKROOT"/scripts/* "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/conf/
cd "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/bin
./stop-cluster.sh

rm "$FLINKROOT"/build-target/log/*
cd "$FLINKROOT"/scripts/
while IFS= read -r line; do
  ip="$line"
  printf '%s\n' $ip
  iplist+=("$line")
done < workers

for ip in "${iplist[@]}"
do
  if [[ $ip != $localip ]]; then
    printf '%s\n' '-----------------------------------------------------'
    echo $ip
    ssh "$ip" "rm -rf "$FLINKROOT""
    ssh "$ip" "mkdir "$FLINKROOT""
    ssh "$ip" "mkdir "$FLINKROOT"/flinkstate/"
    ssh "$ip" "mkdir "$FLINKROOT"/flink-dist/"
    ssh "$ip" "mkdir "$FLINKROOT"/flink-dist/target"
    scp -r "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/ "$ip":"$FLINKROOT"/flink-dist/target/
  fi
done

cd "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/bin
./start-cluster.sh

