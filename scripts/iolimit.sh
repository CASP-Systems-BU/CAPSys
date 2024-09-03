#!/bin/bash

# ./iolimit.sh ~/data/tmp.dat

set -ex

fname=$1

while(true)
do
  # 8GB tmpfile
  sudo taskset -ac 1 dd if=/dev/zero of="$fname" bs=100000 count=80000 conv=notrunc
  rm -rf "$fname"
done
