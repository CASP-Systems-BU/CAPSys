#!/bin/bash

TC=/sbin/tc
IF=ens33
LIMIT=50mbit

DST_CIDR=192.168.1.150/24
U32="$TC filter add dev $IF protocol ip parent 1:0 prio 1 u32"

create () {
  $TC qdisc add dev $IF root handle 1:0 htb default 30
  $TC class add dev $IF parent 1:0 classid 1:1 htb rate $LIMIT
  $U32 match ip dst $DST_CIDR flowid 1:1
  printf 'created\n'
}

clean () {
  $TC qdisc del dev $IF root
  printf 'cleaned\n'
}


if [[ "$1" == "create" ]]
then
    create
else
    clean
fi

#clean
#create
