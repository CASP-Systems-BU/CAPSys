#!/bin/bash
export FLINKROOT=$(builtin cd ..; pwd)
echo $FLINKROOT

iplist=()

cd "$FLINKROOT"/scripts/
while IFS= read -r line; do
  ip="$line"
  printf '%s\n' $ip
  iplist+=("$line")
done < workers

for ip in "${iplist[@]}"
do
  printf '%s\n' '-----------------------------------------------------'
  echo $ip
  ssh "$ip" "mkdir "$FLINKROOT""
  scp -r "$FLINKROOT"/scripts "$ip":"$FLINKROOT"/
  if [[ "$1" == "create" ]]
  then
    ssh "$ip" "cd "$FLINKROOT"/scripts; pwd; echo 1 | sudo -S sh -c './tcconfig.sh create'"
  else
    ssh "$ip" "cd "$FLINKROOT"/scripts; pwd; echo 1 | sudo -S sh -c './tcconfig.sh'"
  fi
done
