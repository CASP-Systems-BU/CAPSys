#!/bin/bash
export FLINKROOT=$(builtin cd ..; pwd)
echo $FLINKROOT
iplist=()

timestamp=$(date +%s)

mkdir "$FLINKROOT"/scripts/flinklogs_"$timestamp"
cd "$FLINKROOT"/scripts/

mkdir "$FLINKROOT"/scripts/flinklogs_"$timestamp"/jobmaster
cp "$FLINKROOT"/build-target/log/*  "$FLINKROOT"/scripts/flinklogs_"$timestamp"/jobmaster/

while IFS= read -r line; do
  ip="$line"
  printf '%s\n' $ip
  iplist+=("$line")
done < workers

for ip in "${iplist[@]}"
do
  printf '%s\n' '-----------------------------------------------------'
  echo $ip
  ifname="${ip//\./\_}"
  echo $ifname
  mkdir "$FLINKROOT"/scripts/flinklogs_"$timestamp"/"$ifname"/
  scp "$ip":"$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/log/* "$FLINKROOT"/scripts/flinklogs_"$timestamp"/"$ifname"/
done


mv  "$FLINKROOT"/scripts/flinklogs_* /home/tidb/Desktop/toshiba/flinklogs/
